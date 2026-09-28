"""
REAL LOGIC — FastAPI Dependency Injection.
"""
from __future__ import annotations

from fastapi import HTTPException, Request, status

from app.state import TwinStore


def get_store(request: Request) -> TwinStore:
    """Dependency to fetch TwinStore from application state."""
    store: TwinStore | None = getattr(request.app.state, "store", None)
    if store is None or not store.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CyRIS backend is initializing warm-up simulation.",
        )
    return store
