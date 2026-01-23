from fastapi import FastAPI
from contextlib import asynccontextmanager

import app.models

from .orm import create_tables
from .routers import cars, purchases, users
from .auth import jwt



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación: Creando tablas en SQLite...")
    await create_tables()
    yield
    print("Apagando aplicación...")

app = FastAPI(
    title="Luxury Car Shop API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(cars.router)
app.include_router(purchases.router)
app.include_router(jwt.router)
app.include_router(users.router)

@app.get("/")
async def read_root():
    return {
        "status": "OK",
        "message": "API de Luxury Car Shop funcionando"
    }
