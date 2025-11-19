from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SaleItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float


class SaleItem(SaleItemBase):
    id: int

    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    branch_id: int
    client_id: Optional[int] = None
    items: List[SaleItemBase]
    cash: float = 0
    kaspi: float = 0
    credit: float = 0
    payment_type: str = "cash"


class SaleCreate(SaleBase):
    pass


class Sale(SaleBase):
    id: int
    seller_id: int
    total: float
    created_at: datetime
    updated_at: datetime
    items: List[SaleItem]

    class Config:
        from_attributes = True
