from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_current_user
from app.database.session import get_db
from app.models.entities import Client, Debt, Product, Return, Sale, SaleItem, Stock, User
from app.schemas import returns as return_schema
from app.services.inventory import adjust_stock

router = APIRouter()


@router.get("/", response_model=list[return_schema.Return])
async def list_returns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Return).order_by(Return.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=return_schema.Return, status_code=status.HTTP_201_CREATED)
async def create_return(
    payload: return_schema.ReturnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sale = await db.get(Sale, payload.sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    sale_item = await db.execute(
        select(SaleItem).where(SaleItem.sale_id == sale.id, SaleItem.product_id == payload.product_id)
    )
    sale_item = sale_item.scalar_one_or_none()
    if not sale_item or sale_item.quantity < payload.quantity:
        raise HTTPException(status_code=400, detail="Invalid return quantity")
    product = await db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.quantity += payload.quantity
    await adjust_stock(db, sale.branch_id, payload.product_id, payload.quantity)
    return_entry = Return(
        sale_id=sale.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        amount=payload.amount,
        processed_by=current_user.id,
    )
    db.add(return_entry)
    if sale.credit > 0 and sale.client_id:
        client = await db.get(Client, sale.client_id)
        if client:
            client.total_debt = max(client.total_debt - payload.amount, 0)
    await db.commit()
    await db.refresh(return_entry)
    return return_entry
