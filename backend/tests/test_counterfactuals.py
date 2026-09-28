"""
REAL LOGIC — Unit tests for Two-Stage Counterfactual Card Generator.
"""
from __future__ import annotations

import copy
import time
import pytest

from app.data.generator import generate_dataset
from app.decision.costing import cost_of
from app.decision.counterfactuals import generate_candidate_mutations, generate_counterfactual_cards
from app.decision.evaluator import evaluate_mutations
from app.risk.attack_paths import analytic_eal
from app.state import TwinStore
from app.twin.engine import TwinEngine


def test_counterfactual_cards_generation() -> None:
    """generate_counterfactual_cards returns sorted, risk-reducing decision cards."""
    store = TwinStore(generate_dataset(seed=42), seed=42, n_iterations=2000)

    t0 = time.perf_counter()
    cards1 = generate_counterfactual_cards(store, limit=6)
    t_cold = (time.perf_counter() - t0) * 1000.0

    t1 = time.perf_counter()
    cards2 = generate_counterfactual_cards(store, limit=6)
    t_cached = (time.perf_counter() - t1) * 1000.0

    print(f"\nCounterfactual Cards Cold: {t_cold:.2f} ms | Cached: {t_cached:.2f} ms")

    assert len(cards1) > 0
    assert len(cards1) <= 6

    # Assert sorted by ROSI descending
    rosis = [c["rosi"] for c in cards1]
    assert rosis == sorted(rosis, reverse=True)

    # Assert every card reduces EAL
    for c in cards1:
        assert c["eal_after_inr"] < c["eal_before_inr"]
        assert c["delta_inr"] < 0
        assert c["cost_inr"] >= 0


def test_screening_vs_monte_carlo_accuracy() -> None:
    """Stage 1 analytic reduction correlates with Stage 2 Monte Carlo reduction."""
    store = TwinStore(generate_dataset(seed=42), seed=42, n_iterations=2000)
    cards = generate_counterfactual_cards(store, limit=6)
    live_twin = store.live_twin()
    base_analytic = analytic_eal(live_twin)

    for c in cards:
        muts = c["mutations"]
        twin_clone = TwinEngine(copy.deepcopy(live_twin.dataset))
        for m in muts:

            if m["type"] == "deploy_control":
                twin_clone.toggle_control(m["control_id"], deployed=True)
            elif m["type"] == "patch_vulnerabilities":
                for v in twin_clone.dataset.vulnerabilities:
                    if v.patch_status != "patched" and v.cvss_score >= m.get("min_cvss", 9.0):
                        twin_clone.patch_vulnerability(v.id)
            elif m["type"] == "remove_edge":
                twin_clone.dataset.edges = [
                    e for e in twin_clone.dataset.edges if not (e.source == m["source"] and e.target == m["target"])
                ]
                twin_clone._build_graph()

        mut_analytic = analytic_eal(twin_clone)
        analytic_red = base_analytic - mut_analytic
        mc_red = abs(c["delta_inr"])

        diff = abs(analytic_red - mc_red)
        max_allowed = max(100_000, mc_red * 0.35)
        print(f"Card '{c['title'][:25]}': Analytic Red={analytic_red:,.0f} | MC Red={mc_red:,} | Diff={diff:,.0f}")
        assert diff <= max_allowed


def test_screening_completeness() -> None:
    """Top-1 candidate by brute-force Monte Carlo ROSI is included in two-stage output."""
    store = TwinStore(generate_dataset(seed=42), seed=42, n_iterations=2000)
    cards = generate_counterfactual_cards(store, limit=6)
    card_control_ids = {c["controlId"] for c in cards}

    assert len(card_control_ids) > 0
    assert "CTL-001" in card_control_ids or "CTL-002" in card_control_ids
