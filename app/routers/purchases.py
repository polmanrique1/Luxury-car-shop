from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.Purchase import Purchase
from app.orm import async_session_maker
from app.schemas.purchase_schemas import PurchaseCreate, PurchaseResponse

router = APIRouter(prefix="/purchases", tags=["Purchases"])

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/")
async def get_all_purchases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Purchase))
    purchases = result.scalars().all()
    return purchases


@router.get("/{id}")
async def get_purchase_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Purchase).where(Purchase.id == id))
    purchase = result.scalar_one_or_none()
    
    if not purchase:
        raise HTTPException(status_code=404,detail= "This purchase do not exists")
    
    return purchase

@router.get("/user/{userId}")
async def get_user_purchases(userId: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Purchase).where(Purchase.user_id == userId))
    user_purchases = result.scalars().all()
    
    if not user_purchases :
        return {"message": "This user do not have purchases"}
    
    return user_purchases

@router.post("/", response_model=PurchaseResponse)
async def add_purchase(newPurchase: PurchaseCreate ,db: AsyncSession = Depends(get_db)): 
    try:
        new_purchase = Purchase(
                car_id= newPurchase.car_id,
                user_id= newPurchase.user_id
            )
        
        db.add(new_purchase)
        await db.commit()
        await db.refresh(new_purchase)

        return new_purchase
    except HTTPException as e:
        return {"message": "something gone wrong during the insertion"}

@router.delete("/{id}")
async def delete_purchase(id: int, db: AsyncSession = Depends(get_db)):

    result = db.execute(select(Purchase).where(Purchase.id == id))
    purchase_to_delete = result.scalar_one_or_none()

    db.delete(purchase_to_delete)

    return {"message": "purchase deleted successfly"}