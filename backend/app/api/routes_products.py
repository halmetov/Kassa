from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import get_current_user, require_admin, require_employee
from app.database.session import get_db
from app.models.entities import Branch, Product, Stock
from app.models.user import User
from app.schemas import stock as stock_schema
from app.schemas import products as product_schema
from app.services.files import save_upload

router = APIRouter(redirect_slashes=False)


@router.get("", response_model=list[product_schema.Product], dependencies=[Depends(require_employee)])
async def list_products(
    branch_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_branch_id = branch_id
    if current_user.role == "employee":
        target_branch_id = current_user.branch_id
        if target_branch_id is None:
            raise HTTPException(status_code=400, detail="Сотрудник не привязан к филиалу")

    query = select(Product)
    if target_branch_id is not None:
        query = (
            query.join(Stock, Stock.product_id == Product.id)
            .where(Stock.branch_id == target_branch_id)
            .distinct()
        )

    result = db.execute(query)
    return result.scalars().all()


@router.post("", response_model=product_schema.Product, dependencies=[Depends(require_employee)])
async def create_product(payload: product_schema.ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=product_schema.Product, dependencies=[Depends(require_employee)])
async def update_product(product_id: int, payload: product_schema.ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return None


@router.post("/{product_id}/photo", response_model=product_schema.Product, dependencies=[Depends(require_admin)])
async def upload_photo(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    photo_path = await save_upload(file)
    product.photo = photo_path
    product.image_url = photo_path
    db.commit()
    db.refresh(product)
    return product


@router.get("/low-stock", response_model=list[stock_schema.LowStockItem], dependencies=[Depends(require_employee)])
async def low_stock(
    branch_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_branch_id = branch_id
    if current_user.role == "employee":
        target_branch_id = current_user.branch_id
        if target_branch_id is None:
            raise HTTPException(status_code=400, detail="Сотрудник не привязан к филиалу")

    query = (
        select(Stock, Product, Branch)
        .join(Product, Stock.product_id == Product.id)
        .join(Branch, Stock.branch_id == Branch.id)
        .where(Stock.quantity < Product.limit)
    )
    if target_branch_id is not None:
        query = query.where(Stock.branch_id == target_branch_id)

    result = db.execute(query)
    items: list[stock_schema.LowStockItem] = []
    for stock, product, branch in result.all():
        items.append(
            stock_schema.LowStockItem(
                id=product.id,
                name=product.name,
                branch=branch.name,
                quantity=stock.quantity,
                limit=product.limit or 0,
            )
        )
    return items
