from datetime import date, datetime, time
from decimal import Decimal
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.auth.security import get_current_user, require_employee, require_admin
from app.core.enums import UserRole
from app.database.session import get_db
from app.models.entities import Branch, Expense
from app.models.user import User
from app.schemas.expenses import ExpenseCreate, ExpenseOut

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)


def _get_date_range(start_date: date | None, end_date: date | None) -> tuple[datetime, datetime]:
    today = date.today()
    start = datetime.combine(start_date or today, time.min)
    end_boundary = end_date or today
    end = datetime.combine(end_boundary, time.max)
    return start, end


def _resolve_branch_id(current_user: User, branch_id: int | None) -> int | None:
    role_value = current_user.role.value if isinstance(current_user.role, UserRole) else current_user.role
    if role_value == UserRole.ADMIN.value:
        return branch_id

    user_branch_id = current_user.branch_id
    if user_branch_id is None:
        raise HTTPException(status_code=400, detail="Сотрудник не привязан к филиалу")
    if branch_id is None:
        return user_branch_id
    if branch_id != user_branch_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для этого филиала")
    return branch_id


@router.get("", response_model=list[ExpenseOut], dependencies=[Depends(require_employee)])
async def list_expenses(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_dt, end_dt = _get_date_range(start_date, end_date)
    branch_id = _resolve_branch_id(current_user, None)
    query = (
        select(Expense)
        .options(joinedload(Expense.created_by))
        .where(Expense.created_at >= start_dt, Expense.created_at <= end_dt)
        .order_by(Expense.created_at.desc())
    )
    if branch_id is not None:
        query = query.where(Expense.branch_id == branch_id)
    expenses = db.execute(query).scalars().unique().all()
    return [
        ExpenseOut.model_validate(
            expense,
            from_attributes=True,
            update={"created_by_name": expense.created_by.name if expense.created_by else None},
        )
        for expense in expenses
    ]


@router.post(
    "",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_employee)],
)
async def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    branch_id = _resolve_branch_id(current_user, payload.branch_id)
    if branch_id is not None:
        branch = db.get(Branch, branch_id)
        if branch is None:
            raise HTTPException(status_code=400, detail="Филиал не найден")

    try:
        expense = Expense(
            title=payload.title,
            amount=Decimal(str(payload.amount)),
            created_by_id=current_user.id,
            branch_id=branch_id,
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to create expense", exc_info=exc)
        raise HTTPException(status_code=500, detail="Не удалось сохранить расход") from exc

    return ExpenseOut.model_validate(
        expense,
        from_attributes=True,
        update={"created_by_name": current_user.name},
    )


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Расход не найден")
    db.delete(expense)
    db.commit()
    return None
