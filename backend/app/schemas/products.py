from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    category_id: Optional[int] = None
    unit: str = "pcs"
    barcode: Optional[str] = None
    purchase_price: float = 0
    sale_price: float = 0
    wholesale_price: float = 0
    limit: int = 0
    image_url: Optional[str] = None
    photo: Optional[str] = None


class ProductCreate(ProductBase):
    class Config:
        extra = "ignore"


class ProductUpdate(ProductBase):
    class Config:
        extra = "ignore"


class Product(ProductBase):
    id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
