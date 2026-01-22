from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from ..models.Car import Car
from ..orm import async_session_maker
from ..schemas.car_schemas import CarCreate, CarResponse


router = APIRouter(prefix="/cars", tags=["Cars"])

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/", response_model=List[CarResponse]) 
async def get_cars(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car))
    car_list = result.scalars().all()
    return car_list

@router.get("/{id}")
async def get_car_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car).where(Car.id == id))
    car = result.scalar_one_or_none()
    return car

@router.get("/brand/{brand}")
async def get_cars_by_brand(brand: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car).where(Car.brand == brand))
    cars = result.scalars().all()

    if not cars:
        raise HTTPException(status_code=404, detail="There are no cars with this brand")
    return cars


@router.post("/", response_model=CarResponse) 
async def create_car(car_data: CarCreate, db: AsyncSession = Depends(get_db)):
    new_car = Car(**car_data.model_dump())
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car) 
    return new_car

@router.delete("/{id}")
async def delete_car(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car).where(Car.id == id))
    car_to_delete = result.scalar_one_or_none()

    if not car_to_delete:
        raise HTTPException(status_code=404, detail="Car not found")

    await db.delete(car_to_delete)
    return {"message": "Car seccesfuly deleted"}