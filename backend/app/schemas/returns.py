from datetime import datetime

from pydantic import BaseModel


class ReturnCreate(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    amount: float


class Return(ReturnCreate):
    id: int
    processed_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
