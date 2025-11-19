from datetime import datetime
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


class SaleItemDetail(SaleItem):
    product_name: Optional[str] = None
    product_unit: Optional[str] = None


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


class SaleDetail(BaseModel):
    id: int
    created_at: datetime
    branch_id: int
    branch_name: Optional[str] = None
    seller_id: int
    seller_name: Optional[str] = None
    client_id: Optional[int] = None
    client_name: Optional[str] = None
    cash: float
    kaspi: float
    credit: float
    payment_type: str
    total: float
    items: List[SaleItemDetail]
