from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.orm import Base

class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    car_id: Mapped[int] = mapped_column(
        ForeignKey("cars.id"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    car = relationship("Car")
    user = relationship("User")
