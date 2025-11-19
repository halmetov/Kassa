from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database.session import get_db
from app.models.entities import Client, Debt, Product, Sale, SaleItem, Stock, User
from app.schemas import sales as sales_schema
from app.services.inventory import adjust_stock

router = APIRouter()


@router.get("/", response_model=list[sales_schema.Sale])
async def list_sales(db: Session = Depends(get_db)):
    result = db.execute(select(Sale).order_by(Sale.created_at.desc()))
    sales = result.scalars().unique().all()
    for sale in sales:
        db.refresh(sale, attribute_names=["items"])
    return sales


@router.post("/", response_model=sales_schema.Sale, status_code=status.HTTP_201_CREATED)
async def create_sale(
    payload: sales_schema.SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sale = Sale(
        branch_id=payload.branch_id,
        seller_id=current_user.id,
        client_id=payload.client_id,
        cash=payload.cash,
        kaspi=payload.kaspi,
        credit=payload.credit,
        payment_type=payload.payment_type,
        total=0,
    )
    db.add(sale)
    db.flush()
    total = 0
    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        stock = db.execute(
            select(Stock).where(Stock.branch_id == payload.branch_id, Stock.product_id == item.product_id)
        )
        stock_row = stock.scalar_one_or_none()
        if not stock_row or stock_row.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        adjust_stock(db, payload.branch_id, item.product_id, -item.quantity)
        product.quantity = max(product.quantity - item.quantity, 0)
        sale_item = SaleItem(sale_id=sale.id, product_id=item.product_id, quantity=item.quantity, price=item.price)
        db.add(sale_item)
        total += item.price * item.quantity
    sale.total = total
    if payload.credit > 0 and payload.client_id:
        client = db.get(Client, payload.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        client.total_debt += payload.credit
        debt = Debt(client_id=client.id, sale_id=sale.id, amount=payload.credit)
        db.add(debt)
    db.commit()
    db.refresh(sale)
    db.refresh(sale, attribute_names=["items"])
    return sale
