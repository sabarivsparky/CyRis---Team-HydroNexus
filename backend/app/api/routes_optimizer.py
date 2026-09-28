"""
REAL LOGIC — Budget Optimizer API Routes.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_store
from app.config import OPTIMIZER_MAX_BUDGET_INR
from app.decision.options import build_options
from app.decision.optimizer import build_pareto_frontier, run_optimizer
from app.decision.portfolio import PortfolioEvaluator
from app.state import TwinStore

router = APIRouter()


@router.get("/optimizer/options")
def get_optimizer_options_route(
    store: TwinStore = Depends(get_store),
) -> dict[str, Any]:
    """Return catalog of atomic purchasable options and dropped candidates."""
    live_twin = store.live_twin()
    active_opts, dropped_opts = build_options(live_twin)
    return {
        "options": [o.model_dump() for o in active_opts],
        "dropped": [d.model_dump() for d in dropped_opts],
        "twin_fingerprint": store.get_fingerprint(live_twin),
    }


@router.get("/optimizer/frontier")
def get_optimizer_frontier_route(
    store: TwinStore = Depends(get_store),
) -> dict[str, Any]:
    """Return complete Pareto frontier curve pre-evaluated on the living twin."""
    live_twin = store.live_twin()
    active_opts, _ = build_options(live_twin)
    options_map = {o.id: o.model_dump() for o in active_opts}

    evaluator = PortfolioEvaluator(live_twin, active_opts)
    frontier, solver_used, exact, eval_count, compute_ms = build_pareto_frontier(evaluator, active_opts)

    return {
        "frontier": frontier,
        "options": options_map,
        "baseline_eal_inr": int(evaluator.base_eal),
        "meta": {
            "solver_used": solver_used,
            "exact": exact,
            "subsets_evaluated": eval_count,
            "compute_ms": compute_ms,
            "twin_fingerprint": store.get_fingerprint(live_twin),
            "max_budget_inr": OPTIMIZER_MAX_BUDGET_INR,
        },
    }


@router.post("/optimizer/run")
def run_optimizer_route(
    payload: dict[str, Any],
    store: TwinStore = Depends(get_store),
) -> dict[str, Any]:
    """Run budget optimization for requested budget ceiling and verify via Monte Carlo."""
    budget_inr = payload.get("budget_inr")

    if budget_inr is None or not isinstance(budget_inr, int) or budget_inr <= 0 or budget_inr > OPTIMIZER_MAX_BUDGET_INR:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"budget_inr must be an integer between 1 and {OPTIMIZER_MAX_BUDGET_INR:,}.",
        )

    try:
        return run_optimizer(store, budget_inr=budget_inr)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err),
        )
