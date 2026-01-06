from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_user, require_workshop_only
from app.database.session import get_db
from app.models import (
    Branch,
    Income,
    IncomeItem,
    Product,
    Stock,
    User,
    WorkshopEmployee,
    WorkshopOrder,
    WorkshopOrderClosure,
    WorkshopOrderMaterial,
    WorkshopOrderPayout,
)
from app.schemas import branches as branch_schema
from app.schemas import workshop as workshop_schema
from app.services.files import save_upload
from app.services.inventory import adjust_stock

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
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workshop branch not found",
        )
    return branch


@router.get("/branch", response_model=branch_schema.Branch)
def get_workshop_branch(db: Session = Depends(get_db)) -> Branch:
    return _get_workshop_branch(db)


@router.get("/employees", response_model=list[workshop_schema.WorkshopEmployeeOut])
def list_employees(search: Optional[str] = Query(None, alias="q"), db: Session = Depends(get_db)):
    query = db.query(WorkshopEmployee)
    if search:
        term = f"%{search}%"
        query = query.filter(
            (WorkshopEmployee.first_name.ilike(term))
            | (WorkshopEmployee.last_name.ilike(term))
            | (WorkshopEmployee.phone.ilike(term))
            | (WorkshopEmployee.position.ilike(term))
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
        setattr(employee, field, value.strip() if isinstance(value, str) else value)
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


@router.get("/employees/search", response_model=list[workshop_schema.WorkshopEmployeeSearchOut])
def search_employees(q: Optional[str] = Query(None, alias="q"), db: Session = Depends(get_db)):
    query = db.query(WorkshopEmployee).filter(WorkshopEmployee.active.is_(True))
    if q:
        term = f"%{q}%"
        query = query.filter(
            (WorkshopEmployee.first_name.ilike(term))
            | (WorkshopEmployee.last_name.ilike(term))
            | (WorkshopEmployee.phone.ilike(term))
            | (WorkshopEmployee.position.ilike(term))
        )
    employees = query.order_by(WorkshopEmployee.id.desc()).all()
    results: list[workshop_schema.WorkshopEmployeeSearchOut] = []
    for employee in employees:
        full_name = " ".join(filter(None, [employee.first_name, employee.last_name]))
        results.append(
            workshop_schema.WorkshopEmployeeSearchOut(
                id=employee.id,
                full_name=full_name.strip() or employee.first_name,
                phone=employee.phone,
                salary_total=employee.total_salary,
                position=employee.position,
            )
        )
    return results


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


def _get_order(db: Session, order_id: int) -> WorkshopOrder:
    order = db.get(WorkshopOrder, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return order


def _serialize_order_detail(order: WorkshopOrder, db: Session) -> workshop_schema.WorkshopOrderDetail:
    db.refresh(order, attribute_names=["materials", "payouts"])
    material_rows: list[workshop_schema.WorkshopOrderMaterialDetail] = []
    for material in order.materials:
        product = db.get(Product, material.product_id)
        material_rows.append(
            workshop_schema.WorkshopOrderMaterialDetail(
                id=material.id,
                product_id=material.product_id,
                quantity=material.quantity,
                unit=material.unit,
                created_at=material.created_at,
                product_name=product.name if product else "",
                product_barcode=product.barcode if product else None,
            )
        )
    payout_rows: list[workshop_schema.WorkshopOrderPayoutDetail] = []
    for payout in order.payouts:
        employee = db.get(WorkshopEmployee, payout.employee_id)
        full_name = " ".join(
            filter(None, [employee.first_name if employee else None, employee.last_name if employee else None])
        ).strip()
        payout_rows.append(
            workshop_schema.WorkshopOrderPayoutDetail(
                id=payout.id,
                employee_id=payout.employee_id,
                amount=payout.amount,
                note=payout.note,
                created_at=payout.created_at,
                employee_name=full_name or (employee.first_name if employee else ""),
                employee_phone=employee.phone if employee else None,
                employee_position=employee.position if employee else None,
            )
        )
    return workshop_schema.WorkshopOrderDetail(
        id=order.id,
        title=order.title,
        amount=order.amount,
        customer_name=order.customer_name,
        description=order.description,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
        closed_at=order.closed_at,
        branch_id=order.branch_id,
        photo=order.photo,
        paid_amount=order.paid_amount,
        materials=material_rows,
        payouts=payout_rows,
    )


def _assert_order_open(order: WorkshopOrder) -> None:
    if order.status == "closed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order is closed")


@router.get("/orders/{order_id}", response_model=workshop_schema.WorkshopOrderDetail)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = _get_order(db, order_id)
    return _serialize_order_detail(order, db)


@router.put("/orders/{order_id}", response_model=workshop_schema.WorkshopOrderOut)
def update_order(order_id: int, payload: workshop_schema.WorkshopOrderUpdate, db: Session = Depends(get_db)):
    order = _get_order(db, order_id)
    _assert_order_open(order)
    if payload.status == "closed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Use close endpoint to close order")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = _get_order(db, order_id)
    db.delete(order)
    db.commit()
    return None


@router.post("/orders/{order_id}/photo", response_model=workshop_schema.WorkshopOrderOut)
async def upload_order_photo(
    order_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    order = _get_order(db, order_id)
    _assert_order_open(order)
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл не передан")
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Разрешена только загрузка изображений")

    photo_name = await save_upload(file, subdir="workshop_orders")
    public_url = f"{str(request.base_url).rstrip('/')}/static/{photo_name}"
    order.photo = public_url
    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/{order_id}/materials", response_model=workshop_schema.WorkshopMaterialOut, status_code=status.HTTP_201_CREATED)
def add_material(order_id: int, payload: workshop_schema.WorkshopMaterialCreate, db: Session = Depends(get_db)):
    order = _get_order(db, order_id)
    _assert_order_open(order)
    workshop_branch = _get_workshop_branch(db)
    if order.branch_id != workshop_branch.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Можно списывать только со склада цеха")
    if payload.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be positive")
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
    _get_order(db, order_id)
    return (
        db.query(WorkshopOrderMaterial)
        .filter(WorkshopOrderMaterial.order_id == order_id)
        .order_by(WorkshopOrderMaterial.created_at.desc())
        .all()
    )


@router.post("/orders/{order_id}/payouts", response_model=workshop_schema.WorkshopPayoutOut, status_code=status.HTTP_201_CREATED)
def add_payout(order_id: int, payload: workshop_schema.WorkshopPayoutCreate, db: Session = Depends(get_db)):
    order = _get_order(db, order_id)
    _assert_order_open(order)
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
    _get_order(db, order_id)
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
    order = _get_order(db, order_id)
    if payload.paid_amount < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="paid_amount must be non-negative")
    if order.status == "closed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order is closed")
    now = datetime.utcnow()
    order.status = "closed"
    order.closed_at = now
    order.paid_amount = payload.paid_amount
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


@router.get("/income/products", response_model=list[workshop_schema.WorkshopIncomeProduct])
def workshop_income_products(
    search: Optional[str] = Query(None, alias="q"), db: Session = Depends(get_db)
):
    query = db.query(Product)
    if search:
        term = f"%{search}%"
        query = query.filter((Product.name.ilike(term)) | (Product.barcode.ilike(term)))
    products = query.order_by(Product.name.asc()).limit(50).all()
    return [
        workshop_schema.WorkshopIncomeProduct(
            id=product.id,
            name=product.name,
            unit=product.unit,
            barcode=product.barcode,
            photo=product.photo or product.image_url,
            purchase_price=product.purchase_price,
            sale_price=product.sale_price,
        )
        for product in products
    ]


@router.post(
    "/income",
    response_model=workshop_schema.WorkshopIncomeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workshop_income(
    payload: workshop_schema.WorkshopIncomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    branch = _get_workshop_branch(db)
    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет товаров для прихода")
    income = Income(branch_id=branch.id, created_by_id=current_user.id)
    db.add(income)
    db.flush()
    stock_updates: list[workshop_schema.WorkshopIncomeStock] = []
    for item in payload.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be positive")
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found",
            )
        income_item = IncomeItem(
            income_id=income.id,
            product_id=item.product_id,
            quantity=item.quantity,
            purchase_price=item.purchase_price,
            sale_price=item.sale_price,
        )
        db.add(income_item)
        product.quantity += item.quantity
        product.purchase_price = item.purchase_price
        product.sale_price = item.sale_price
        stock = adjust_stock(db, branch.id, item.product_id, item.quantity)
        stock_updates.append(
            workshop_schema.WorkshopIncomeStock(
                product_id=item.product_id, branch_id=branch.id, quantity=stock.quantity
            )
        )
    db.commit()
    db.refresh(income)
    db.refresh(income, attribute_names=["items"])
    return workshop_schema.WorkshopIncomeResponse(income=income, stock=stock_updates)


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


def _get_workshop_stock(search: Optional[str], db: Session) -> list[workshop_schema.WorkshopStockProduct]:
    branch = _get_workshop_branch(db)
    query = db.query(Stock).join(Stock.product).filter(Stock.branch_id == branch.id)
    if search:
        term = f"%{search}%"
        query = query.filter(
            (Stock.product.has())
            & ((Stock.product.name.ilike(term)) | (Stock.product.barcode.ilike(term)))
        )
    items: list[workshop_schema.WorkshopStockProduct] = []
    for stock in query.all():
        items.append(
            workshop_schema.WorkshopStockProduct(
                product_id=stock.product_id,
                name=stock.product.name if stock.product else "",
                available_qty=stock.quantity,
                unit=stock.product.unit if stock.product else None,
                barcode=stock.product.barcode if stock.product else None,
                photo=stock.product.photo or (stock.product.image_url if stock.product else None),
                limit=stock.product.limit if stock.product else None,
                purchase_price=stock.product.purchase_price if stock.product else None,
            )
        )
    return items


@router.get("/stock/products", response_model=list[workshop_schema.WorkshopStockProduct])
def workshop_stock_products(search: Optional[str] = Query(None, alias="q"), db: Session = Depends(get_db)):
    return _get_workshop_stock(search, db)


@router.get("/products", response_model=list[workshop_schema.WorkshopStockProduct])
def workshop_products(search: Optional[str] = Query(None, alias="q"), db: Session = Depends(get_db)):
    return _get_workshop_stock(search, db)


@router.get("/stock", response_model=list[workshop_schema.WorkshopStockProduct])
def workshop_stock(search: Optional[str] = Query(None, alias="q"), db: Session = Depends(get_db)):
    return _get_workshop_stock(search, db)
