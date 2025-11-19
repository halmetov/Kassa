from datetime import datetime

from pydantic import BaseModel


class Stock(BaseModel):
    id: int
    branch_id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
