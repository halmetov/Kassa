from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ClientBase(BaseModel):
    name: str
    phone: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class Client(ClientBase):
    id: int
    total_debt: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
