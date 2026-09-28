"""
REAL LOGIC — Two-Stage Counterfactual Card Generator.

Executes fast deterministic analytic screening (Stage 1) followed by rigorous
Monte Carlo confirmation (Stage 2) using Common Random Numbers (CRN) to produce ranked,
quantified decision cards.
"""
from __future__ import annotations

import copy
import hashlib
import json
import time
from typing import Any

from app.config import (
    COUNTERFACTUAL_RETURN_TOP_K,
    COUNTERFACTUAL_SCREEN_TOP_M,
)
from app.decision.costing import cost_of, compute_financial_metrics
from app.decision.evaluator import apply_mutation_to_twin, evaluate_mutations
from app.risk.attack_paths import analytic_eal, chokepoints
from app.state import TwinStore
from app.twin.engine import TwinEngine

_CARD_CACHE: dict[str, list[dict[str, Any]]] = {}


def format_inr_short(amount: int) -> str:
    """Format integer INR monetary amount into short human-readable string (Lakhs / Crores)."""
    abs_amt = abs(amount)
    sign = "-" if amount < 0 else ""

    if abs_amt >= 10_000_000:
        cr = round(abs_amt / 10_000_000.0, 2)
        return f"{sign}₹{cr} Cr"
    elif abs_amt >= 100_000:
        lakh = round(abs_amt / 100_000.0, 1)
        return f"{sign}₹{lakh} Lakhs"
    else:
        return f"{sign}₹{abs_amt:,}"


def generate_candidate_mutations(twin: TwinEngine) -> list[tuple[str, str, list[dict[str, Any]]]]:
    """Generate candidate action tuples: (title, control_id, mutations_list)."""
    candidates: list[tuple[str, str, list[dict[str, Any]]]] = []

    # 1. Candidate controls
    for ctrl in twin.dataset.controls:
        if ctrl.status == "candidate":
            title = f"Deploy {ctrl.name}"
            muts = [{"type": "deploy_control", "control_id": ctrl.id}]
            candidates.append((title, ctrl.id, muts))

    # 2. Patch actions
    candidates.append(
        (
            "Remediate All Critical Vulnerabilities (CVSS >= 9.0)",
            "patch-critical",
            [{"type": "patch_vulnerabilities", "min_cvss": 9.0}],
        )
    )

    # 3. Chokepoint severance actions
    cps = chokepoints(twin, limit=3)
    for cp in cps:
        if not cp.control_already_deployed and cp.suggested_control_id:
            # Skip if already covered by candidate control card
            if any(c[1] == cp.suggested_control_id for c in candidates):
                continue

        title = f"Sever Exploit Path {cp.source} → {cp.target}"
        muts = [{"type": "remove_edge", "source": cp.source, "target": cp.target}]
        candidates.append((title, cp.suggested_control_id or "sever-edge", muts))

    return candidates


def generate_counterfactual_cards(
    store: TwinStore,
    limit: int = COUNTERFACTUAL_RETURN_TOP_K,
) -> list[dict[str, Any]]:
    """Two-Stage Counterfactual Card Generator (Analytic Screen + Monte Carlo Confirm)."""
    t0 = time.perf_counter()
    live_twin = store.live_twin()
    fp = store.get_fingerprint(live_twin)

    # Cache hit check
    if fp in _CARD_CACHE:
        return _CARD_CACHE[fp][:limit]

    base_analytic_eal = analytic_eal(live_twin)
    candidates = generate_candidate_mutations(live_twin)

    # STAGE 1: Analytic Screen (Fast deterministic screening)
    stage1_results: list[tuple[float, str, str, list[dict[str, Any]]]] = []

    for title, ctrl_id, muts in candidates:
        try:
            twin_clone = TwinEngine(copy.deepcopy(live_twin.dataset))
            for m in muts:
                apply_mutation_to_twin(twin_clone, m)

            mut_analytic_eal = analytic_eal(twin_clone)
            reduction = base_analytic_eal - mut_analytic_eal
            if reduction <= 0:
                continue

            c_breakdown = cost_of(live_twin, muts)
            c_cost = c_breakdown.total_inr
            screen_rosi = (reduction - c_cost) / float(c_cost) if c_cost > 0 else (reduction / float(max(1, base_analytic_eal)))

            stage1_results.append((screen_rosi, title, ctrl_id, muts))
        except ValueError:
            continue

    # Sort Stage 1 by analytic ROSI desc and pick top M
    stage1_results.sort(key=lambda item: item[0], reverse=True)
    top_candidates = stage1_results[:COUNTERFACTUAL_SCREEN_TOP_M]

    # STAGE 2: Monte Carlo Confirmation (Rigorous CRN Simulation)
    cards: list[dict[str, Any]] = []

    for _, title, ctrl_id, muts in top_candidates:
        try:
            eval_res = evaluate_mutations(store, muts)

            before_eal = eval_res["before_eal_inr"]
            after_eal = eval_res["after_eal_inr"]
            delta = eval_res["delta_inr"]
            delta_ratio = eval_res["delta_ratio"]
            cost = eval_res["cost_inr"]
            rosi = eval_res["rosi"]
            payback = eval_res["payback_months"]

            # Compute stable card ID
            mut_json = json.dumps(muts, sort_keys=True)
            card_id = hashlib.sha256(f"{fp}:{mut_json}".encode()).hexdigest()[:12]

            pct_str = f"{abs(int(delta_ratio * 100))}%"
            action_text = (
                f"{title}: cuts EAL from {format_inr_short(before_eal)} to {format_inr_short(after_eal)} "
                f"({format_inr_short(delta)}, {pct_str}) for {format_inr_short(cost)}; ROSI {rosi if rosi is not None else 0}x."
            )

            cards.append(
                {
                    "card_id": card_id,
                    "id": card_id,
                    "controlId": ctrl_id,
                    "title": title,
                    "action": action_text,
                    "proposedAction": action_text,
                    "mutations": muts,
                    "eal_before_inr": before_eal,
                    "eal_after_inr": after_eal,
                    "delta_inr": delta,
                    "delta_ratio": delta_ratio,
                    "var95_before_inr": eval_res["var95_before_inr"],
                    "var95_after_inr": eval_res["var95_after_inr"],
                    "cost_inr": cost,
                    "cost_breakdown": eval_res["cost_breakdown"],
                    "rosi": rosi if rosi is not None else 0.0,
                    "payback_months": payback,
                    "top_asset_deltas": eval_res["top_asset_deltas"][:3],
                    "twin_fingerprint": fp,
                    "computed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )
        except ValueError:
            continue

    # Rank Stage 2 by Monte Carlo ROSI descending
    cards.sort(key=lambda c: c["rosi"] if c["rosi"] is not None else -999.0, reverse=True)
    _CARD_CACHE[fp] = cards

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return cards[:limit]
