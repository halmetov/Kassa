from datetime import date, datetime
from typing import List

from pydantic import BaseModel


class SaleSummary(BaseModel):
    id: int
    created_at: datetime
    seller: str
    branch: str
    total: float
    payment_type: str


class DailyReport(BaseModel):
    day: date
    total_sales: float
    total_credit: float


class StaffReport(BaseModel):
    seller: str
    total: float


class BranchReport(BaseModel):
    branch: str
    total: float


class ReportsResponse(BaseModel):
    sales: List[SaleSummary]
    by_day: List[DailyReport]
    by_seller: List[StaffReport]
    by_branch: List[BranchReport]
