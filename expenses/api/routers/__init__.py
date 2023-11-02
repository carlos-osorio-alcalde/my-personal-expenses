from expenses.api.routers.database import router as database_router
from expenses.api.routers.expenses import router as expenses_router
from expenses.api.routers.merchants import router as merchants_router
from expenses.api.routers.monitoring import router as monitoring_router

__all__ = [
    "expenses_router",
    "merchants_router",
    "database_router",
    "monitoring_router",
]
