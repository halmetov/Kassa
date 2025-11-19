from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import require_role
from app.database.session import get_db
from app.models.entities import Branch, Product, Stock
from app.schemas import branches as branch_schema

router = APIRouter()


@router.get("/", response_model=list[branch_schema.Branch])
async def list_branches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Branch))
    return result.scalars().all()


@router.post("/", response_model=branch_schema.Branch, dependencies=[Depends(require_role("admin"))])
async def create_branch(payload: branch_schema.BranchCreate, db: AsyncSession = Depends(get_db)):
    branch = Branch(**payload.dict())
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch


@router.put("/{branch_id}", response_model=branch_schema.Branch, dependencies=[Depends(require_role("admin"))])
async def update_branch(branch_id: int, payload: branch_schema.BranchUpdate, db: AsyncSession = Depends(get_db)):
    branch = await db.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(branch, field, value)
    await db.commit()
    await db.refresh(branch)
    return branch


@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("admin"))])
async def delete_branch(branch_id: int, db: AsyncSession = Depends(get_db)):
    branch = await db.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    await db.delete(branch)
    await db.commit()
    return None


@router.get("/{branch_id}/stock")
async def branch_stock(branch_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Stock, Product.name)
        .join(Product, Stock.product_id == Product.id)
        .where(Stock.branch_id == branch_id)
    )
    response = []
    for stock, product_name in result.all():
        response.append(
            {
                "id": stock.id,
                "product_id": stock.product_id,
                "product": product_name,
                "quantity": stock.quantity,
                "limit": stock.product.limit if stock.product else None,
            }
        )
    return response
