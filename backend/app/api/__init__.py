"""
REAL LOGIC — API Routers package init.
"""
from app.api.routes_health import router as health_router
from app.api.routes_risk import router as risk_router

__all__ = ["health_router", "risk_router"]
