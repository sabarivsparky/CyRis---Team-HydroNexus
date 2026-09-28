"""
REAL LOGIC — FastAPI Application Factory & Lifespan Manager.

Boots the CyRIS backend, warms up the TwinStore baseline simulation, backfills
trend history, and registers CORS, API routers, and error handlers.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health_router, risk_router
from app.api.routes_optimizer import router as optimizer_router
from app.api.routes_paths import router as paths_router
from app.api.routes_twin import router as twin_router
from app.api.routes_whatif import router as whatif_router
from app.config import API_PREFIX, CORS_ORIGINS, CYRIS_N_ITERATIONS, CYRIS_SEED
from app.data.generator import generate_dataset
from app.errors import register_error_handlers
from app.state import TwinStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cyris.main")


def init_store() -> TwinStore:
    """Initialize dataset and TwinStore baseline state."""
    logger.info(f"Initializing CyRIS TwinStore (seed={CYRIS_SEED}, n_iterations={CYRIS_N_ITERATIONS})...")
    dataset = generate_dataset(seed=CYRIS_SEED)
    store = TwinStore(dataset=dataset, seed=CYRIS_SEED, n_iterations=CYRIS_N_ITERATIONS)
    logger.info(f"TwinStore ready. Baseline warm-up runtime: {store.baseline_runtime_ms:.2f} ms")
    return store


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """App lifespan context manager."""
    if not hasattr(app.state, "store") or app.state.store is None:
        app.state.store = init_store()
    yield
    logger.info("CyRIS backend shutting down.")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="CyRIS Backend Engine",
        version="0.1.0",
        description="Cyber Risk Information System — Actuarial Quantification & Living Digital Twin API",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Initialize store immediately so TestClient / background runs are ready
    app.state.store = init_store()

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Error envelope handlers
    register_error_handlers(app)

    # Register API Routers under API_PREFIX (/api/v1)
    app.include_router(health_router, prefix=API_PREFIX, tags=["Health"])
    app.include_router(risk_router, prefix=API_PREFIX, tags=["Risk"])
    app.include_router(twin_router, prefix=API_PREFIX, tags=["Twin Graph"])
    app.include_router(paths_router, prefix=API_PREFIX, tags=["Attack Paths"])
    app.include_router(whatif_router, prefix=API_PREFIX, tags=["What-If & Counterfactuals"])
    app.include_router(optimizer_router, prefix=API_PREFIX, tags=["Budget Optimizer"])

    return app



app = create_app()
