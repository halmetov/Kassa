from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class WorkshopEmployeeBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    active: bool = True


class WorkshopEmployeeCreate(WorkshopEmployeeBase):
    pass


class WorkshopEmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    active: Optional[bool] = None


class WorkshopEmployeeOut(WorkshopEmployeeBase):
    id: int
    total_salary: Decimal = Field(default=Decimal("0"))
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkshopOrderBase(BaseModel):
    title: str
    amount: Decimal = Field(default=Decimal("0"))
    customer_name: Optional[str] = None
    description: Optional[str] = None


class WorkshopOrderCreate(WorkshopOrderBase):
    pass


class WorkshopOrderUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[Decimal] = None
    customer_name: Optional[str] = None
    description: Optional[str] = None


class WorkshopOrderOut(WorkshopOrderBase):
    id: int
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    closed_at: Optional[datetime]
    branch_id: Optional[int]

    class Config:
        from_attributes = True


class WorkshopMaterialCreate(BaseModel):
    product_id: int
    quantity: Decimal
    unit: Optional[str] = None


class WorkshopMaterialOut(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkshopPayoutCreate(BaseModel):
    employee_id: int
    amount: Decimal
    note: Optional[str] = None


class WorkshopPayoutOut(BaseModel):
    id: int
    employee_id: int
    amount: Decimal
    note: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkshopClosePayload(BaseModel):
    paid_amount: Decimal
    note: Optional[str] = None


class WorkshopClosureOut(BaseModel):
    id: int
    order_id: int
    order_amount: Decimal
    paid_amount: Decimal
    note: Optional[str]
    closed_at: Optional[datetime]
    closed_by_user_id: Optional[int]

    class Config:
        from_attributes = True


class WorkshopReportFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
