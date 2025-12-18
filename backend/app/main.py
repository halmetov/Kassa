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
    routes_pos,
    routes_returns,
    routes_movements,
    routes_sales,
    routes_users,
)
from app.core.config import get_settings
from app.database.session import SessionLocal
from app.database.migrations import run_migrations_on_startup
from app.auth.security import get_password_hash
from app.models.user import User

import app.models  # noqa: F401 - ensure models are imported for metadata

settings = get_settings()

app = FastAPI(title="Kassa API", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    run_migrations_on_startup(settings)

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.login == "admin").first()
        if admin is None:
            new_admin = User(
                name="Admin",
                login="admin",
                password_hash=get_password_hash("admin"),
                role="admin",
                active=True,
            )
            db.add(new_admin)
            db.commit()
    finally:
        db.close()

ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://192.168.8.98:8080",  # TODO: replace with the active frontend origin if different
    "http://10.221.89.109:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
app.include_router(routes_pos.router, prefix="/api/pos", tags=["pos"])
app.include_router(routes_reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(routes_returns.router, prefix="/api/returns", tags=["returns"])
app.include_router(routes_movements.router, prefix="/api/movements", tags=["movements"])

media_root = settings.media_root_path
media_root.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=media_root), name="static")


@app.get("/health", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
