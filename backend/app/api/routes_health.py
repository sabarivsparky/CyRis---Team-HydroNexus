"""
REAL LOGIC — Health & Status Routes.
"""
from __future__ import annotations

import time

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_store
from app.state import TwinStore

router = APIRouter()


@router.get("/health")
def health_check(request: Request, store: TwinStore = Depends(get_store)) -> dict:
    """Return comprehensive system health and warm-up status."""
    twin = store.live_twin()
    uptime = round(time.time() - store.start_time, 2)

    return {
        "status": "ok",
        "ready": store.is_ready,
        "version": "0.1.0",
        "seed": store.seed,
        "n_iterations": store.n_iterations,
        "twin_version": 1,
        "twin_fingerprint": store.get_fingerprint(twin),
        "asset_count": len(twin.dataset.assets),
        "baseline_runtime_ms": store.baseline_runtime_ms,
        "optimizer_ready": True,
        "uptime_s": uptime,
    }

