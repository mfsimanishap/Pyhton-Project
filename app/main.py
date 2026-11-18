"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config.log_config import configure_logging
from app.routers.auth import router as auth_router
from app.routers.deductions import router as deductions_router
from app.routers.salary import router as salary_router
from app.routers.system import router as system_router
from app.routers.tax import router as tax_router
from app.routers.taxpayer import router as taxpayer_router

configure_logging()

app = FastAPI(
    title="Income Tax Calculator API",
    description="API for calculating and comparing Indian income tax.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(system_router)
app.include_router(taxpayer_router)
app.include_router(salary_router)
app.include_router(deductions_router)
app.include_router(tax_router)
