from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..models import User
from ..orm import async_session_maker

router = APIRouter(prefix="/auth", tags=["auth"])

# ======================
# CONFIG JWT
# ======================
SECRET_KEY = "a44c77g8d9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

# ======================
# SCHEMAS
# ======================
class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

# ======================
# DB DEPENDENCY
# ======================
async def get_db():
    async with async_session_maker() as session:
        yield session


db_dependency = Annotated[AsyncSession, Depends(get_db)]

# ======================
# UTILS PASSWORD (SIN HASH)
# ======================
def get_password_hash(password: str) -> str:
    # Devuelve la contraseña tal cual, solo para pruebas
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compara directamente la contraseña en texto plano
    return plain_password == hashed_password

# ======================
# JWT FUNCTIONS
# ======================
def create_access_token(username: str, user_id: int, expires_delta: timedelta | None = None):
    to_encode = {
        "sub": username,
        "id": user_id
    }

    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

# ======================
# AUTH LOGIC
# ======================
async def authenticate_user(username: str, password: str, db: AsyncSession):
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user

# ======================
# ENDPOINTS
# ======================
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_request: CreateUserRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(User).where(User.username == user_request.username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )

    new_user = User(
        username=user_request.username,
        email=user_request.email,
        password=get_password_hash(user_request.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "Usuario creado exitosamente"}

@router.post("/login", response_model=Token)
async def login(login_request: LoginRequest, db: AsyncSession = Depends(get_db)):
    
    user = await authenticate_user(login_request.username, login_request.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        username=user.username,
        user_id=user.id
    )

    return { "access_token": access_token, "token_type": "bearer" }


async def get_current_user(
    token: str = Depends(oauth2_bearer),
    db: AsyncSession = Depends(get_db)
):
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("id")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return user


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email
    }
