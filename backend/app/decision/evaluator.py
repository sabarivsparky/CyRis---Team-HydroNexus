"""
REAL LOGIC — Shared Scenario Evaluator.

Clones the living twin, applies mutations, re-simulates using Common Random Numbers (CRN),
and evaluates financial risk reduction, ROSI, and payback.
"""
from __future__ import annotations

import copy
import time
from typing import Any

from app.decision.costing import cost_of, compute_financial_metrics
from app.state import TwinStore
from app.twin.engine import TwinEngine


def apply_mutation_to_twin(twin: TwinEngine, mutation: dict[str, Any]) -> None:
    """Apply a single mutation dictionary to a TwinEngine instance."""
    m_type = mutation.get("type") or mutation.get("action")

    if m_type == "deploy_control":
        cid = mutation.get("control_id") or mutation.get("controlId")
        if not cid or cid not in twin.control_map:
            raise ValueError(f"Unknown control_id '{cid}' in mutation.")
        ctrl = twin.control_map[cid]
        if ctrl.status == "deployed":
            raise ValueError(f"Control '{cid}' ({ctrl.name}) is already deployed.")
        twin.toggle_control(cid, deployed=True)

    elif m_type == "remove_control":
        cid = mutation.get("control_id") or mutation.get("controlId")
        if not cid or cid not in twin.control_map:
            raise ValueError(f"Unknown control_id '{cid}' in mutation.")
        twin.toggle_control(cid, deployed=False)

    elif m_type in ("patch_vulnerability", "patch_vulnerabilities"):
        vid = mutation.get("vulnerability_id") or mutation.get("vulnId")
        min_cvss = mutation.get("min_cvss")
        asset_id = mutation.get("asset_id")

        if vid:
            if vid not in twin.vuln_map:
                raise ValueError(f"Unknown vulnerability_id '{vid}' in mutation.")
            twin.patch_vulnerability(vid)
        elif min_cvss is not None or asset_id is not None:
            matched = [
                v for v in twin.dataset.vulnerabilities
                if v.patch_status != "patched"
                and (min_cvss is None or v.cvss_score >= min_cvss)
                and (asset_id is None or v.asset_id == asset_id)
            ]
            for v in matched:
                twin.patch_vulnerability(v.id)

    elif m_type == "delay_patch":
        vid = mutation.get("vulnerability_id") or mutation.get("vulnId")
        days = mutation.get("days", 30)
        if vid:
            if vid not in twin.vuln_map:
                raise ValueError(f"Unknown vulnerability_id '{vid}' in mutation.")
            twin.delay_patch(vid, days=days)
        else:
            # Apply to all open vulnerabilities
            open_vulns = [v for v in twin.dataset.vulnerabilities if v.patch_status != "patched"]
            for v in open_vulns:
                twin.delay_patch(v.id, days=days)

    elif m_type in ("remove_edge", "scale_edge_probability"):
        src = mutation.get("source") or mutation.get("src")
        tgt = mutation.get("target") or mutation.get("tgt")
        twin.dataset.edges = [
            e for e in twin.dataset.edges if not (e.source == src and e.target == tgt)
        ]
        twin._build_graph()

    else:
        raise ValueError(f"Unknown mutation type '{m_type}'.")


def evaluate_mutations(
    store: TwinStore,
    mutations: list[dict[str, Any]],
    n: int | None = None,
) -> dict[str, Any]:
    """REAL LOGIC. Clone live twin -> mutate clone -> re-simulate with Common Random Numbers."""
    t0 = time.perf_counter()
    live_twin = store.live_twin()
    before_res = store.baseline() if (n is None or n == store.n_iterations) else store.result_for(live_twin, n=n)
    before_eal = before_res.org.eal_inr
    before_v95 = before_res.org.var95_inr
    before_v99 = before_res.org.var99_inr

    # Clone twin and apply mutations
    after_twin = TwinEngine(copy.deepcopy(live_twin.dataset))
    for m in mutations:
        apply_mutation_to_twin(after_twin, m)

    fp_before = store.get_fingerprint(live_twin)
    fp_after = store.get_fingerprint(after_twin)

    # No-op detection
    if fp_before == fp_after:
        raise ValueError("Mutation(s) change nothing: dataset fingerprint identical to baseline.")

    # Re-simulate with same seed & N (Common Random Numbers)
    after_res = store.result_for(after_twin, n=n)
    after_eal = after_res.org.eal_inr
    after_v95 = after_res.org.var95_inr
    after_v99 = after_res.org.var99_inr

    cost_breakdown = cost_of(live_twin, mutations)
    cost_total = cost_breakdown.total_inr

    reduction_inr, delta_ratio, rosi, payback_months = compute_financial_metrics(
        before_eal, after_eal, cost_total
    )

    # Top asset EAL deltas
    before_asset_map = {ar.asset_id: ar for ar in before_res.assets}
    after_asset_map = {ar.asset_id: ar for ar in after_res.assets}

    asset_deltas: list[dict[str, Any]] = []
    for a_id, b_ar in before_asset_map.items():
        a_ar = after_asset_map.get(a_id)
        a_eal = a_ar.eal_inr if a_ar else 0
        diff = a_eal - b_ar.eal_inr
        asset_deltas.append(
            {
                "asset_id": a_id,
                "name": b_ar.name,
                "eal_before_inr": b_ar.eal_inr,
                "eal_after_inr": a_eal,
                "delta_inr": diff,
            }
        )

    asset_deltas.sort(key=lambda d: abs(d["delta_inr"]), reverse=True)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    return {
        "before_eal_inr": before_eal,
        "after_eal_inr": after_eal,
        "delta_inr": after_eal - before_eal,
        "delta_ratio": delta_ratio,
        "var95_before_inr": before_v95,
        "var95_after_inr": after_v95,
        "var99_before_inr": before_v99,
        "var99_after_inr": after_v99,
        "cost_inr": cost_total,
        "cost_breakdown": [
            {"label": item.label, "amount_inr": item.amount_inr} for item in cost_breakdown.items
        ],
        "rosi": rosi,
        "payback_months": payback_months,
        "top_asset_deltas": asset_deltas[:10],
        "twin_fingerprint_before": fp_before,
        "twin_fingerprint_after": fp_after,
        "n_iterations": n or store.n_iterations,
        "seed": store.seed,
        "runtime_ms": elapsed_ms,
    }
