import logging
import sys
from contextlib import asynccontextmanager

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
    routes_cashier,
    routes_users,
)
from app.bootstrap import bootstrap
from app.core.config import get_settings
from app.core.errors import register_error_handlers

import app.models  # noqa: F401 - ensure models are imported for metadata

settings = get_settings()
logger = logging.getLogger(__name__)

# Configure root logger for better debugging (useful for login errors, etc.)
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: running bootstrap")
    try:
        bootstrap(settings)
    except Exception:
        logger.exception("Application bootstrap failed")
        raise
    yield
    logger.info("Application shutdown complete")


app = FastAPI(title="Kassa API", version="1.0.0", redirect_slashes=False, lifespan=lifespan)
app.router.redirect_slashes = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_origin_regex=settings.allowed_cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)

register_error_handlers(app)

app.include_router(routes_auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(routes_users.router, prefix="/api/users", tags=["users"])
app.include_router(routes_categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(routes_products.router, prefix="/api/products", tags=["products"])
app.include_router(routes_branches.router, prefix="/api/branches", tags=["branches"])
app.include_router(routes_income.router, prefix="/api/income", tags=["income"])
app.include_router(routes_sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(routes_clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(routes_pos.router, prefix="/api/pos", tags=["pos"])
app.include_router(routes_cashier.router, prefix="/api/cashier", tags=["cashier"])
app.include_router(routes_reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(routes_returns.router, prefix="/api/returns", tags=["returns"])
app.include_router(routes_movements.router, prefix="/api/movements", tags=["movements"])

media_root = settings.media_root_path
media_root.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=media_root), name="static")


@app.get("/api/health", tags=["system"])
def api_healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
