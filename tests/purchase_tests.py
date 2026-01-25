import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models import Car, Purchase, User
from app.orm import async_session_maker
from app.services import budget_service
from app.services import email
import asyncio

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def db_session():
    async with async_session_maker() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# --- TESTS ---

async def test_get_all_purchases_empty(test_client: AsyncClient, db_session: AsyncSession):
    await db_session.execute("DELETE FROM purchases")
    await db_session.commit()

    response = await test_client.get("/purchases/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

async def test_get_purchase_by_id_not_found(test_client: AsyncClient):
    response = await test_client.get("/purchases/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "This purchase do not exists"

async def test_get_user_purchases_empty(test_client: AsyncClient, db_session: AsyncSession):
    response = await test_client.get("/purchases/user/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "This user do not have purchases"

async def test_make_purchase_success(test_client: AsyncClient, db_session: AsyncSession, monkeypatch):
    user = User(username="buyer", email="buyer@example.com", password="secret")
    car = Car(brand="BMW", model="X5", year=2022, price=50000)
    db_session.add_all([user, car])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(car)

    async def fake_current_user():
        return user
    monkeypatch.setattr("app.routers.purchases.get_current_user", fake_current_user)

    async def fake_payment(amount, user_id, db):
        return True
    monkeypatch.setattr(budget_service, "payment", fake_payment)

    def fake_send_mail(email_addr, car_obj):
        return True
    monkeypatch.setattr(email, "send_mail", fake_send_mail)

    payload = {"car_id": car.id}
    response = await test_client.post("/purchases/", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["car_id"] == car.id
    assert data["user_id"] == user.id

async def test_delete_purchase_success(test_client: AsyncClient, db_session: AsyncSession):
    purchase = Purchase(car_id=1, user_id=1)
    db_session.add(purchase)
    await db_session.commit()
    await db_session.refresh(purchase)

    response = await test_client.delete(f"/purchases/{purchase.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "purchase deleted successfly"
