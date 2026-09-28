"""
REAL LOGIC — What-If Simulation Sandbox & Counterfactual Cards Routes.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_store
from app.config import (
    COUNTERFACTUAL_RETURN_TOP_K,
    WHATIF_MAX_MUTATIONS,
    WHATIF_N_MAX,
    WHATIF_N_MIN,
)
from app.decision.counterfactuals import generate_counterfactual_cards
from app.decision.evaluator import evaluate_mutations
from app.decision.presets import get_all_presets, get_preset
from app.schemas import CounterfactualCard, WhatIfResult
from app.state import TwinStore

router = APIRouter()


@router.get("/whatif/presets")
def get_presets_route() -> list[dict[str, Any]]:
    """Return list of pre-configured what-if preset scenarios."""
    return get_all_presets()


@router.post("/whatif")
def simulate_whatif_route(
    payload: dict[str, Any],
    store: TwinStore = Depends(get_store),
) -> dict[str, Any]:
    """Execute custom or preset what-if simulation against cloned living twin."""
    preset_id = payload.get("preset")
    mutations = payload.get("mutations")
    n_iter = payload.get("n_iterations")

    if (preset_id is None and not mutations) or (preset_id is not None and mutations):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request must specify exactly one of 'preset' or 'mutations'.",
        )

    if n_iter is not None:
        if not (WHATIF_N_MIN <= n_iter <= WHATIF_N_MAX):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"n_iterations must be between {WHATIF_N_MIN:,} and {WHATIF_N_MAX:,}.",
            )

    if preset_id:
        preset = get_preset(preset_id)
        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preset '{preset_id}' not found.",
            )
        mutations = preset["mutations"]

    if len(mutations) > WHATIF_MAX_MUTATIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Exceeded max allowed mutations limit of {WHATIF_MAX_MUTATIONS}.",
        )

    try:
        eval_res = evaluate_mutations(store, mutations=mutations, n=n_iter)
        return eval_res
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err),
        )


@router.get("/counterfactuals")
def get_counterfactuals_route(
    limit: int = Query(COUNTERFACTUAL_RETURN_TOP_K, ge=1, le=20, description="Max cards to return"),
    store: TwinStore = Depends(get_store),
) -> list[dict[str, Any]]:
    """Return ranked, quantified counterfactual decision cards."""
    return generate_counterfactual_cards(store, limit=limit)
