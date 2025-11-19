from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import require_role
from app.database.session import get_db
from app.models.entities import Product
from app.schemas import products as product_schema
from app.services.files import save_upload

router = APIRouter()


@router.get("/", response_model=list[product_schema.Product])
async def list_products(db: Session = Depends(get_db)):
    result = db.execute(select(Product))
    return result.scalars().all()


@router.post("/", response_model=product_schema.Product, dependencies=[Depends(require_role("admin"))])
async def create_product(payload: product_schema.ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=product_schema.Product, dependencies=[Depends(require_role("admin"))])
async def update_product(product_id: int, payload: product_schema.ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return None


@router.post("/{product_id}/photo", response_model=product_schema.Product, dependencies=[Depends(require_role("admin"))])
async def upload_photo(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    photo_path = await save_upload(file)
    product.photo = photo_path
    db.commit()
    db.refresh(product)
    return product
