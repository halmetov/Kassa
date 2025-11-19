from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import (
    routes_auth,
    routes_branches,
    routes_categories,
    routes_clients,
    routes_income,
    routes_products,
    routes_reports,
    routes_returns,
    routes_sales,
    routes_users,
)
from app.core.config import get_settings
from app.database.base import Base
from app.database.session import engine

import app.models  # noqa: F401 - ensure models are imported for metadata

settings = get_settings()

app = FastAPI(title="Kassa API", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(routes_users.router, prefix="/api/users", tags=["users"])
app.include_router(routes_categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(routes_products.router, prefix="/api/products", tags=["products"])
app.include_router(routes_branches.router, prefix="/api/branches", tags=["branches"])
app.include_router(routes_income.router, prefix="/api/income", tags=["income"])
app.include_router(routes_sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(routes_clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(routes_reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(routes_returns.router, prefix="/api/returns", tags=["returns"])

app.mount("/static", StaticFiles(directory=settings.media_root), name="static")


@app.get("/health", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
