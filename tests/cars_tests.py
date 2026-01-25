import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.Car import Car
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

async def test_create_car(test_client: AsyncClient):
    payload = {"brand": "Toyota", "model": "Corolla", "year": 2020}
    response = await test_client.post("/cars/", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["brand"] == "Toyota"
    assert data["model"] == "Corolla"

async def test_get_cars(test_client: AsyncClient):
    response = await test_client.get("/cars/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

async def test_get_car_by_id(test_client: AsyncClient, db_session: AsyncSession):
    
    new_car = Car(brand="Honda", model="Civic", year=2019)
    db_session.add(new_car)
    await db_session.commit()
    await db_session.refresh(new_car)

    response = await test_client.get(f"/cars/{new_car.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == new_car.id
    assert data["brand"] == "Honda"

async def test_get_cars_by_brand(test_client: AsyncClient, db_session: AsyncSession):

    car1 = Car(brand="Ford", model="Focus", year=2018)
    car2 = Car(brand="Ford", model="Fiesta", year=2017)
    db_session.add_all([car1, car2])
    await db_session.commit()

    response = await test_client.get("/cars/brand/Ford")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    assert all(car["brand"] == "Ford" for car in data)

    response = await test_client.get("/cars/brand/UnknownBrand")
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def test_delete_car(test_client: AsyncClient, db_session: AsyncSession):
    car = Car(brand="Mazda", model="3", year=2021)
    db_session.add(car)
    await db_session.commit()
    await db_session.refresh(car)

    response = await test_client.delete(f"/cars/{car.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Car seccesfuly deleted"

    response = await test_client.delete("/cars/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
