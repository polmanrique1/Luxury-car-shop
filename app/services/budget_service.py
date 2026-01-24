from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.Budget import Budget
from app.orm import async_session_maker



async def get_db():
    async with async_session_maker() as session:
        yield session


async def add_mony(quantity: float, user_id: int, db: AsyncSession):
    result = await db.execute(select(Budget).where(Budget.user_id == user_id))
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(status_code=404, detail="This budget does not exist")

    budget.money += quantity

    await db.commit()
    await db.refresh(budget)

    return budget

async def payment(quantity: float, id: int, db: AsyncSession):
    result = await db.execute(select(Budget).where(Budget.user_id == id))
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found for this user")

    if budget.money < quantity:
        raise HTTPException( status_code=400,  detail=f"Insufficient funds. Required: {quantity}, Available: {budget.money}")


    budget.money -= quantity

    
    await db.flush() 
    
    return budget



