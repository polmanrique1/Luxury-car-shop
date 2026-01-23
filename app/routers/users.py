from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.User import User
from app.orm import async_session_maker 
from app.auth.jwt import get_current_user


router = APIRouter(prefix="/users", tags=["users"])

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()

    if not users:
        return {"message": "there are no users"}

    return users


@router.delete("/{id}")
async def delete_users(id: int, db: AsyncSession = Depends(get_db), current_user: str = Depends(get_current_user)):
    result = await db.execute(select(User).where(User.id == id))
    user_to_delete = result.scalar_one_or_none()

    if not user_to_delete:
        return {"message": "the user does not exists"}
            
    db.delete(user_to_delete)
    db.commit()

    return {"message": "the user has been deleted successfuly"}
 