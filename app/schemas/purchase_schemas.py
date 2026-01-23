from pydantic import BaseModel
from typing import Optional


class PurchaseCreate(BaseModel):
    car_id: int


class PurchaseResponse(PurchaseCreate):
    id: int

    class Config:
        from_attributes = True