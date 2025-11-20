from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import require_admin, require_employee
from app.database.session import get_db
from app.models.entities import Branch, Product, Stock
from app.schemas import stock as stock_schema
from app.schemas import products as product_schema
from app.services.files import save_upload

router = APIRouter()


@router.get("/", response_model=list[product_schema.Product], dependencies=[Depends(require_employee)])
async def list_products(db: Session = Depends(get_db)):
    result = db.execute(select(Product))
    return result.scalars().all()


@router.post("/", response_model=product_schema.Product, dependencies=[Depends(require_admin)])
async def create_product(payload: product_schema.ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=product_schema.Product, dependencies=[Depends(require_admin)])
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
    db.commit()
    db.refresh(product)
    return product


@router.get("/low-stock", response_model=list[stock_schema.LowStockItem], dependencies=[Depends(require_employee)])
async def low_stock(db: Session = Depends(get_db)):
    result = db.execute(
        select(Stock, Product, Branch)
        .join(Product, Stock.product_id == Product.id)
        .join(Branch, Stock.branch_id == Branch.id)
        .where(Stock.quantity < Product.limit)
    )
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
