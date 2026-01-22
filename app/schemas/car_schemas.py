from pydantic import BaseModel
from typing import Optional


class CarCreate(BaseModel):
    brand: str
    model: str
    price: float
    image: Optional[str] = None
    video: Optional[str] = None


class CarResponse(CarCreate):
    id: int

    class Config:
        from_attributes = True