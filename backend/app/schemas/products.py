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


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    photo: Optional[str]
    quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
