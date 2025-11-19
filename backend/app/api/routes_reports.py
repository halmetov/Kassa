from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import Branch, Sale, User
from app.schemas import reports as report_schema

router = APIRouter()


@router.get("/summary", response_model=report_schema.ReportsResponse)
async def get_summary(db: Session = Depends(get_db)):
    sales_result = db.execute(select(Sale, User.name, Branch.name).join(User).join(Branch))
    sales = []
    for sale, seller_name, branch_name in sales_result.all():
        sales.append(
            report_schema.SaleSummary(
                id=sale.id,
                created_at=sale.created_at,
                seller=seller_name,
                branch=branch_name,
                total=sale.total,
                payment_type=sale.payment_type,
            )
        )
    by_day_query = db.execute(
        select(func.date(Sale.created_at), func.sum(Sale.total), func.sum(Sale.credit)).group_by(func.date(Sale.created_at))
    )
    by_day = [
        report_schema.DailyReport(day=row[0], total_sales=row[1] or 0, total_credit=row[2] or 0)
        for row in by_day_query.all()
    ]
    by_seller_query = db.execute(
        select(User.name, func.sum(Sale.total)).join(Sale, Sale.seller_id == User.id).group_by(User.name)
    )
    by_seller = [report_schema.StaffReport(seller=row[0], total=row[1] or 0) for row in by_seller_query.all()]
    by_branch_query = db.execute(
        select(Branch.name, func.sum(Sale.total)).join(Sale, Sale.branch_id == Branch.id).group_by(Branch.name)
    )
    by_branch = [report_schema.BranchReport(branch=row[0], total=row[1] or 0) for row in by_branch_query.all()]
    return report_schema.ReportsResponse(sales=sales, by_day=by_day, by_seller=by_seller, by_branch=by_branch)
