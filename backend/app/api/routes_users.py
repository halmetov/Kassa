from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_current_user, hash_password, require_role
from app.database.session import get_db
from app.models.entities import User
from app.schemas import users as user_schema

router = APIRouter(dependencies=[Depends(require_role("admin"))])


@router.get("/", response_model=list[user_schema.User])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.post("/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
async def create_user(payload: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(select(User).where(User.login == payload.login))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Login already used")
    user = User(
        name=payload.name,
        login=payload.login,
        role=payload.role,
        active=payload.active,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/{user_id}", response_model=user_schema.User)
async def update_user(user_id: int, payload: user_schema.UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.dict(exclude_unset=True).items():
        if field == "password" and value:
            user.password_hash = hash_password(value)
        elif field != "password":
            setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return None
