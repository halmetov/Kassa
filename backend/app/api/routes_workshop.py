from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.auth.security import get_current_user, require_workshop_only
from app.database.session import get_db
from app.models import (
    Branch,
    Stock,
    User,
    WorkshopEmployee,
    WorkshopOrder,
    WorkshopOrderClosure,
    WorkshopOrderMaterial,
    WorkshopOrderPayout,
)
from app.schemas import workshop as workshop_schema

router = APIRouter(prefix="/api/workshop", dependencies=[Depends(require_workshop_only)])


WORKSHOP_NAME = "Цех"


def _get_workshop_branch(db: Session) -> Branch:
    branch = db.query(Branch).filter(Branch.is_workshop.is_(True)).first()
    if branch:
        return branch
    branch = db.query(Branch).filter(Branch.name == WORKSHOP_NAME).first()
    if branch:
        branch.is_workshop = True
        db.commit()
        db.refresh(branch)
        return branch
    branch = Branch(name=WORKSHOP_NAME, active=True, is_workshop=True)
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.get("/employees", response_model=list[workshop_schema.WorkshopEmployeeOut])
def list_employees(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(WorkshopEmployee)
    if search:
        term = f"%{search}%"
        query = query.filter(
            (WorkshopEmployee.first_name.ilike(term))
            | (WorkshopEmployee.last_name.ilike(term))
            | (WorkshopEmployee.phone.ilike(term))
        )
    return query.order_by(WorkshopEmployee.id.desc()).all()


@router.post("/employees", response_model=workshop_schema.WorkshopEmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(payload: workshop_schema.WorkshopEmployeeCreate, db: Session = Depends(get_db)):
    employee = WorkshopEmployee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.put("/employees/{employee_id}", response_model=workshop_schema.WorkshopEmployeeOut)
def update_employee(employee_id: int, payload: workshop_schema.WorkshopEmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.get(WorkshopEmployee, employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.get(WorkshopEmployee, employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден")
    db.delete(employee)
    db.commit()
    return None


@router.get("/orders", response_model=list[workshop_schema.WorkshopOrderOut])
def list_orders(db: Session = Depends(get_db)):
    branch = _get_workshop_branch(db)
    return (
        db.query(WorkshopOrder)
        .filter(WorkshopOrder.branch_id == branch.id)
        .order_by(WorkshopOrder.created_at.desc())
        .all()
    )


@router.post("/orders", response_model=workshop_schema.WorkshopOrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: workshop_schema.WorkshopOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    branch = _get_workshop_branch(db)
    order = WorkshopOrder(
        title=payload.title,
        amount=payload.amount or Decimal("0"),
        customer_name=payload.customer_name,
        description=payload.description,
        created_by_user_id=current_user.id,
        branch_id=branch.id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def _ensure_open_order(db: Session, order_id: int) -> WorkshopOrder:
    order = db.get(WorkshopOrder, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return order


@router.get("/orders/{order_id}", response_model=workshop_schema.WorkshopOrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return _ensure_open_order(db, order_id)


@router.put("/orders/{order_id}", response_model=workshop_schema.WorkshopOrderOut)
def update_order(order_id: int, payload: workshop_schema.WorkshopOrderUpdate, db: Session = Depends(get_db)):
    order = _ensure_open_order(db, order_id)
    if order.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказ закрыт")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/{order_id}/materials", response_model=workshop_schema.WorkshopMaterialOut, status_code=status.HTTP_201_CREATED)
def add_material(order_id: int, payload: workshop_schema.WorkshopMaterialCreate, db: Session = Depends(get_db)):
    order = _ensure_open_order(db, order_id)
    if order.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказ закрыт")
    workshop_branch = _get_workshop_branch(db)
    if order.branch_id != workshop_branch.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Можно списывать только со склада цеха")
    stock = (
        db.query(Stock)
        .filter(Stock.branch_id == workshop_branch.id, Stock.product_id == payload.product_id)
        .with_for_update()
        .first()
    )
    if not stock or stock.quantity < float(payload.quantity):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно остатков на складе")
    stock.quantity = stock.quantity - float(payload.quantity)
    material = WorkshopOrderMaterial(
        order_id=order.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit=payload.unit,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/orders/{order_id}/materials", response_model=list[workshop_schema.WorkshopMaterialOut])
def list_materials(order_id: int, db: Session = Depends(get_db)):
    _ensure_open_order(db, order_id)
    return (
        db.query(WorkshopOrderMaterial)
        .filter(WorkshopOrderMaterial.order_id == order_id)
        .order_by(WorkshopOrderMaterial.created_at.desc())
        .all()
    )


@router.post("/orders/{order_id}/payouts", response_model=workshop_schema.WorkshopPayoutOut, status_code=status.HTTP_201_CREATED)
def add_payout(order_id: int, payload: workshop_schema.WorkshopPayoutCreate, db: Session = Depends(get_db)):
    order = _ensure_open_order(db, order_id)
    if order.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказ закрыт")
    employee = db.get(WorkshopEmployee, payload.employee_id)
    if not employee or not employee.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сотрудник не найден")
    payout = WorkshopOrderPayout(order_id=order.id, employee_id=employee.id, amount=payload.amount, note=payload.note)
    employee.total_salary = (employee.total_salary or Decimal("0")) + payload.amount
    db.add(payout)
    db.commit()
    db.refresh(payout)
    return payout


@router.get("/orders/{order_id}/payouts", response_model=list[workshop_schema.WorkshopPayoutOut])
def list_payouts(order_id: int, db: Session = Depends(get_db)):
    _ensure_open_order(db, order_id)
    return (
        db.query(WorkshopOrderPayout)
        .filter(WorkshopOrderPayout.order_id == order_id)
        .order_by(WorkshopOrderPayout.created_at.desc())
        .all()
    )


@router.post("/orders/{order_id}/close", response_model=workshop_schema.WorkshopClosureOut)
def close_order(
    order_id: int,
    payload: workshop_schema.WorkshopClosePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = _ensure_open_order(db, order_id)
    if order.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказ уже закрыт")
    now = datetime.utcnow()
    order.status = "closed"
    order.closed_at = now
    closure = WorkshopOrderClosure(
        order_id=order.id,
        order_amount=order.amount or Decimal("0"),
        paid_amount=payload.paid_amount,
        note=payload.note,
        closed_at=now,
        closed_by_user_id=current_user.id,
    )
    db.add(closure)
    db.commit()
    db.refresh(closure)
    return closure


@router.get("/report", response_model=list[workshop_schema.WorkshopClosureOut])
def report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(WorkshopOrderClosure)
    if start_date:
        query = query.filter(WorkshopOrderClosure.closed_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(WorkshopOrderClosure.closed_at <= datetime.combine(end_date, datetime.max.time()))
    return query.order_by(WorkshopOrderClosure.closed_at.desc()).all()


@router.get("/products")
def workshop_products(search: Optional[str] = None, db: Session = Depends(get_db)):
    branch = _get_workshop_branch(db)
    query = db.query(Stock).join(Stock.product).filter(Stock.branch_id == branch.id)
    if search:
        term = f"%{search}%"
        query = query.filter((Stock.product.has()) & ((Stock.product.name.ilike(term)) | (Stock.product.barcode.ilike(term))))
    results = []
    for stock in query.all():
        results.append(
            {
                "product_id": stock.product_id,
                "name": stock.product.name if stock.product else "",
                "quantity": stock.quantity,
                "unit": stock.product.unit if stock.product else None,
                "barcode": stock.product.barcode if stock.product else None,
            }
        )
    return results


@router.get("/stock")
def workshop_stock(search: Optional[str] = None, db: Session = Depends(get_db)):
    return workshop_products(search=search, db=db)
