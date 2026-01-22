from fastapi import FastAPI
from contextlib import asynccontextmanager
from .orm import create_tables
from .routers import cars

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

app.include_router(cars.router, prefix="/cars", tags=["Cars"])

@app.get("/")
async def read_root():
    return {
        "status": "OK",
        "message": "API de Luxury Car Shop funcionando"
    }
