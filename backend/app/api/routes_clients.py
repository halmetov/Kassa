from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import require_role
from app.database.session import get_db
from app.models.entities import Client
from app.schemas import clients as client_schema

router = APIRouter()


@router.get("/", response_model=list[client_schema.Client])
async def list_clients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client))
    return result.scalars().all()


@router.post("/", response_model=client_schema.Client, status_code=status.HTTP_201_CREATED)
async def create_client(payload: client_schema.ClientCreate, db: AsyncSession = Depends(get_db)):
    client = Client(**payload.dict())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.put("/{client_id}", response_model=client_schema.Client)
async def update_client(client_id: int, payload: client_schema.ClientUpdate, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(client, field, value)
    await db.commit()
    await db.refresh(client)
    return client
