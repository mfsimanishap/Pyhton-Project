"""Application factory and startup configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.env_config import DUMMY_DATA_ENABLED
from app.config.log_config import configure_logging, get_logger
from app.database.base import Base
from app.database.connection import engine, SessionLocal
from app.database.seed import seed_dummy_data
from app.routers.auth import router as auth_router
from app.routers.deductions import router as deductions_router
from app.routers.salary import router as salary_router
from app.routers.system import router as system_router
from app.routers.tax import router as tax_router
from app.routers.taxpayer import router as taxpayer_router

logger = get_logger(__name__)


def start_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging()
    logger.info("Starting application...")

    app = FastAPI(
        title="Income Tax Calculator API",
        description="API for calculating and comparing Indian income tax.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(system_router)
    app.include_router(taxpayer_router)
    app.include_router(salary_router)
    app.include_router(deductions_router)
    app.include_router(tax_router)

    # Create tables for direct local startup; Alembic remains authoritative for migrations.
    Base.metadata.create_all(bind=engine)

    if DUMMY_DATA_ENABLED:
        db = SessionLocal()
        try:
            seed_dummy_data(db)
        finally:
            db.close()

    logger.info("Application started successfully")
    return app
