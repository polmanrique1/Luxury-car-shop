from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.orm import async_session_maker
from app.services.budget_service import add_mony
from app.models.Budget import Budget
from app.schemas.deposit_schemas import DepositResponse, DepositUpdate, DepositCreate

router = APIRouter(prefix="/budgets", tags=["budgets"])

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/", response_model=list[DepositResponse])
async def get_budgets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Budget))
    budgets = result.scalars().all()
    return budgets

@router.post("/", response_model=DepositResponse, status_code=201)
async def create_budget(new_deposit: DepositCreate, db: AsyncSession = Depends(get_db)):
    new_budget_entry = Budget(
        money=new_deposit.money,
        user_id=new_deposit.user_id
    )
    
    db.add(new_budget_entry)
    try:
        await db.commit() 
        await db.refresh(new_budget_entry)
    except Exception as e:
        await db.rollback() 
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    return new_budget_entry

@router.put("/{user_id}", response_model=DepositResponse)
async def deposit(update_data: DepositUpdate, user_id: int, db: AsyncSession = Depends(get_db)):
    
    if update_data.money is None:
        raise HTTPException(status_code=400, detail="Money field is required")
        
    budget = await add_mony(update_data.money, user_id, db)
    return budget