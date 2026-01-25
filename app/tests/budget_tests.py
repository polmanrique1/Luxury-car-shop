import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.Budget import Budget
from app.orm import async_session_maker
from app.services import budget_service

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

async def test_get_budgets_empty(test_client: AsyncClient, db_session: AsyncSession):
    await db_session.execute("DELETE FROM budgets")
    await db_session.commit()

    response = await test_client.get("/budgets/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

async def test_create_budget(test_client: AsyncClient, db_session: AsyncSession):
    payload = {"money": 1000, "user_id": 1}
    response = await test_client.post("/budgets/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["money"] == 1000
    assert data["user_id"] == 1

async def test_deposit_success(test_client: AsyncClient, db_session: AsyncSession, monkeypatch):
    # Crear un presupuesto inicial
    budget = Budget(money=500, user_id=2)
    db_session.add(budget)
    await db_session.commit()
    await db_session.refresh(budget)

    async def fake_add_mony(amount, user_id, db):
        budget.money += amount
        await db.commit()
        await db.refresh(budget)
        return budget

    monkeypatch.setattr(budget_service, "add_mony", fake_add_mony)

    payload = {"money": 300}
    response = await test_client.put("/budgets/2", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["money"] == 800  
    assert data["user_id"] == 2

async def test_deposit_missing_money_field(test_client: AsyncClient):
    payload = {} 
    response = await test_client.put("/budgets/2", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Money field is required"
