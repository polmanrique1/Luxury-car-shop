import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.User import User
from app.orm import async_session_maker

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

async def test_get_users_empty(test_client: AsyncClient, db_session: AsyncSession):
    # Asegurarse que no hay usuarios
    await db_session.execute("DELETE FROM users")
    await db_session.commit()

    response = await test_client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "there are no users"}

async def test_get_users_with_data(test_client: AsyncClient, db_session: AsyncSession):

    user = User(username="testuser", email="test@example.com", password="secret")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await test_client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(u["username"] == "testuser" for u in data)

async def test_delete_user_success(test_client: AsyncClient, db_session: AsyncSession, monkeypatch):

    user = User(username="deleteuser", email="delete@example.com", password="secret")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    async def fake_current_user():
        return "admin"
    monkeypatch.setattr("app.routers.users.get_current_user", fake_current_user)

    response = await test_client.delete(f"/users/{user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "the user has been deleted successfuly"

async def test_delete_user_not_found(test_client: AsyncClient, monkeypatch):
    async def fake_current_user():
        return "admin"
    monkeypatch.setattr("app.routers.users.get_current_user", fake_current_user)

    response = await test_client.delete("/users/999999")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "the user does not exists"
