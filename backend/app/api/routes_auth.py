from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_user_by_login,
    verify_password,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas import auth as auth_schema
from jose import JWTError, jwt
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=auth_schema.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = get_user_by_login(db, form_data.username)
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.active:
            raise HTTPException(status_code=400, detail="User disabled")
        access_token = create_access_token({"sub": str(user.id), "role": user.role})
        refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Database error during login for user %s", form_data.username)
        raise HTTPException(status_code=500, detail="Database error during login") from exc
    except Exception as exc:  # pragma: no cover - defensive logging for unexpected errors
        logger.exception("Unexpected error during login for user %s", form_data.username)
        raise HTTPException(status_code=500, detail="Authentication failed") from exc


@router.get("/me", response_model=auth_schema.AuthUser)
async def get_profile(current_user: User = Depends(get_current_user)):
    return auth_schema.AuthUser(
        id=current_user.id,
        login=current_user.login,
        name=current_user.name,
        role=current_user.role,
        active=current_user.active,
        branch_id=current_user.branch_id,
        branch_name=current_user.branch.name if current_user.branch else None,
    )


@router.post("/refresh", response_model=auth_schema.Token)
async def refresh_token(payload: auth_schema.RefreshRequest, db: Session = Depends(get_db)):
    try:
        data = jwt.decode(payload.refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    user_id = data.get("sub")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
