"""
REAL LOGIC — Unit tests for Scenario Evaluator, Costing Model, CRN Exactness, and Presets.
"""
from __future__ import annotations

import pytest

from app.data.generator import generate_dataset
from app.decision.costing import cost_of, compute_financial_metrics
from app.decision.evaluator import evaluate_mutations
from app.decision.presets import get_all_presets, get_preset
from app.state import TwinStore


def test_cost_and_rosi_formulas() -> None:
    """Hand-computed cases for cost, ROSI, and payback period."""
    red_inr, delta_r, rosi, payback = compute_financial_metrics(
        eal_before=42_000_000,
        eal_after=33_500_000,
        cost_inr=1_800_000,
    )

    assert red_inr == 8_500_000
    assert delta_r == -0.2024
    assert rosi == round((8_500_000 - 1_800_000) / 1_800_000.0, 2)
    assert payback == round(1_800_000 / (8_500_000 / 12.0), 1)

    # Cost 0 case -> ROSI is None
    _, _, rosi_zero, payback_zero = compute_financial_metrics(42_000_000, 33_500_000, 0)
    assert rosi_zero is None

    # Negative reduction (risk increased) -> Payback is None
    _, _, rosi_neg, payback_neg = compute_financial_metrics(42_000_000, 48_000_000, 1_000_000)
    assert payback_neg is None


def test_evaluator_mfa_everywhere() -> None:
    """mfa_everywhere preset reduces EAL, yields negative delta_ratio, and computes ROSI."""
    store = TwinStore(generate_dataset(seed=42), seed=42, n_iterations=2000)
    res = evaluate_mutations(store, mutations=[{"type": "deploy_control", "control_id": "CTL-001"}])

    assert res["after_eal_inr"] < res["before_eal_inr"]
    assert res["delta_ratio"] < 0
    assert res["cost_inr"] == 1_800_000
    assert res["rosi"] > 0.0


def test_evaluator_delay_patch_30d() -> None:
    """delay_patch_30d increases EAL, has cost 0, ROSI None, and payback None."""
    store = TwinStore(generate_dataset(seed=42), seed=42, n_iterations=2000)
    res = evaluate_mutations(store, mutations=[{"type": "delay_patch", "days": 30}])

    assert res["after_eal_inr"] >= res["before_eal_inr"]
    assert res["delta_inr"] >= 0
    assert res["cost_inr"] == 0
    assert res["rosi"] is None
    assert res["payback_months"] is None


def test_evaluator_crn_exactness_and_immutability() -> None:
    """Evaluating same mutation twice gives byte-identical results; live twin fingerprint unchanged."""
    store = TwinStore(generate_dataset(seed=42), seed=42, n_iterations=2000)
    fp_before = store.get_fingerprint(store.live_twin())

    muts = [{"type": "deploy_control", "control_id": "CTL-001"}]
    res1 = evaluate_mutations(store, mutations=muts)
    res2 = evaluate_mutations(store, mutations=muts)

    assert res1["after_eal_inr"] == res2["after_eal_inr"]
    assert res1["delta_inr"] == res2["delta_inr"]

    # Live twin fingerprint unchanged
    fp_after = store.get_fingerprint(store.live_twin())
    assert fp_before == fp_after


def test_evaluator_no_op_rejection() -> None:
    """Deploying an already deployed control raises ValueError for no-op."""
    store = TwinStore(generate_dataset(seed=42), seed=42, n_iterations=1000)
    # CTL-007 is deployed by default
    with pytest.raises(ValueError, match="already deployed"):
        evaluate_mutations(store, mutations=[{"type": "deploy_control", "control_id": "CTL-007"}])


def test_presets_registry() -> None:
    """Presets registry lists 7 valid presets."""
    presets = get_all_presets()
    assert len(presets) == 7
    ids = {p["id"] for p in presets}
    assert "mfa_everywhere" in ids
    assert "segment_subnet_b" in ids
    assert "delay_patch_30d" in ids
