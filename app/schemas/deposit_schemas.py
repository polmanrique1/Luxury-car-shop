from pydantic import BaseModel
from typing import Optional

class DepositCreate(BaseModel):
    money: float 
    user_id: int    

class DepositUpdate(BaseModel):
    money: Optional[float] = None

class DepositResponse(BaseModel):
    id: int
    money: float
    user_id: int 

    class Config:
        from_attributes = True