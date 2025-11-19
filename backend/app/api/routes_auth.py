from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_user_by_login,
    hash_password,
    verify_password,
)
from app.database.session import get_db
from app.models.entities import User
from app.schemas import auth as auth_schema
from jose import JWTError, jwt
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/login", response_model=auth_schema.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_login(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.active:
        raise HTTPException(status_code=400, detail="User disabled")
    access_token = create_access_token(user.login)
    refresh_token = create_refresh_token(user.login)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/register", response_model=auth_schema.AuthUser)
async def register_user(payload: auth_schema.RegisterRequest, db: Session = Depends(get_db)):
    existing = get_user_by_login(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Login already exists")
    user = User(
        name=payload.name or payload.username,
        login=payload.username,
        password_hash=hash_password(payload.password),
        role="seller",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=auth_schema.AuthUser)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model=auth_schema.Token)
async def refresh_token(payload: auth_schema.RefreshRequest, db: Session = Depends(get_db)):
    try:
        data = jwt.decode(payload.refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    login = data.get("sub")
    user = get_user_by_login(db, login)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access_token = create_access_token(user.login)
    refresh_token = create_refresh_token(user.login)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
