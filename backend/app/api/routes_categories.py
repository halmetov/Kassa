from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import require_role
from app.database.session import get_db
from app.models.entities import Category
from app.schemas import categories as category_schema

router = APIRouter()


@router.get("/", response_model=list[category_schema.Category])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.post("/", response_model=category_schema.Category, dependencies=[Depends(require_role("admin"))])
async def create_category(payload: category_schema.CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(name=payload.name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.put("/{category_id}", response_model=category_schema.Category, dependencies=[Depends(require_role("admin"))])
async def update_category(category_id: int, payload: category_schema.CategoryUpdate, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = payload.name
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()
    return None
