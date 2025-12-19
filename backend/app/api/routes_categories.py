from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import require_admin, require_employee
from app.database.session import get_db
from app.models.entities import Category
from app.schemas import categories as category_schema

router = APIRouter()


@router.get("", response_model=list[category_schema.Category], dependencies=[Depends(require_employee)])
@router.get("/", response_model=list[category_schema.Category], dependencies=[Depends(require_employee)])
async def list_categories(db: Session = Depends(get_db)):
    result = db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.post("", response_model=category_schema.Category, dependencies=[Depends(require_employee)])
@router.post("/", response_model=category_schema.Category, dependencies=[Depends(require_employee)])
async def create_category(payload: category_schema.CategoryCreate, db: Session = Depends(get_db)):
    category = Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=category_schema.Category, dependencies=[Depends(require_employee)])
async def update_category(category_id: int, payload: category_schema.CategoryUpdate, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = payload.name
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return None
