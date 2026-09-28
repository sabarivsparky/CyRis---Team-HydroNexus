"""
REAL LOGIC — Structural Causal What-If & Counterfactual Intervention Engine.

Simulates security interventions (deploy control, patch vulnerability, delay patch)
and computes baseline vs. mutated EAL, delta risk reduction, cost, and Return on
Security Investment (ROSI).
"""
from __future__ import annotations

import copy
from typing import Any

from app.risk.engine import get_risk_summary
from app.schemas import CounterfactualCard, Dataset, WhatIfRequest, WhatIfResult
from app.twin.engine import TwinEngine


def apply_mutations(dataset: Dataset, mutations: list[dict[str, Any]]) -> tuple[Dataset, int]:
    """Apply a sequence of mutation dictionaries to a dataset copy and calculate total cost."""
    mutated_dataset = copy.deepcopy(dataset)
    twin = TwinEngine(mutated_dataset)
    total_cost = 0

    for mut in mutations:
        m_type = mut.get("type")
        if m_type == "deploy_control":
            cid = mut.get("control_id") or mut.get("controlId")
            if cid:
                twin.toggle_control(cid, deployed=True)
                c_obj = twin.control_map.get(cid)
                if c_obj:
                    total_cost += c_obj.cost_inr
        elif m_type == "patch_vulnerability":
            vid = mut.get("vulnerability_id") or mut.get("vulnId")
            if vid:
                twin.patch_vulnerability(vid)
                total_cost += 50_000  # Nominal engineering patch cost
        elif m_type == "delay_patch":
            vid = mut.get("vulnerability_id")
            days = mut.get("days", 30)
            if vid:
                twin.delay_patch(vid, days=days)

    return twin.dataset, total_cost


def run_what_if_scenario(dataset: Dataset, request: WhatIfRequest) -> WhatIfResult:
    """Simulate a what-if scenario with specified mutations and return risk impact."""
    base_summary = get_risk_summary(dataset, seed=request.seed)
    before_eal = base_summary.eal_inr

    mutated_dataset, cost_inr = apply_mutations(dataset, request.mutations)

    mut_summary = get_risk_summary(mutated_dataset, seed=request.seed)
    after_eal = mut_summary.eal_inr

    delta_inr = after_eal - before_eal
    delta_ratio = round(delta_inr / max(1, before_eal), 4)

    risk_reduction = before_eal - after_eal
    if cost_inr > 0:
        rosi = round((risk_reduction - cost_inr) / cost_inr, 2)
    else:
        rosi = round(risk_reduction / max(1, before_eal), 2)

    return WhatIfResult(
        before_eal_inr=before_eal,
        after_eal_inr=after_eal,
        delta_inr=delta_inr,
        delta_ratio=delta_ratio,
        cost_inr=cost_inr,
        rosi=rosi,
    )


def get_counterfactual_cards(dataset: Dataset, seed: int = 42) -> list[CounterfactualCard]:
    """Generate pre-computed counterfactual decision cards for candidate controls."""
    base_summary = get_risk_summary(dataset, seed=seed)
    before_eal = base_summary.eal_inr

    candidate_controls = [c for c in dataset.controls if c.status == "candidate"]
    cards: list[CounterfactualCard] = []

    for idx, c in enumerate(candidate_controls, start=1):
        req = WhatIfRequest(
            mutations=[{"type": "deploy_control", "control_id": c.id}],
            n_iterations=5_000,
            seed=seed,
        )
        res = run_what_if_scenario(dataset, req)

        action_desc = f"Deploy {c.name} across covered assets"
        cards.append(
            CounterfactualCard(
                id=f"cf-{c.id.lower()}",
                controlId=c.id,
                title=f"Option #{idx}: {c.name}",
                action=action_desc,
                proposedAction=action_desc,
                eal_before_inr=before_eal,
                eal_after_inr=res.after_eal_inr,
                cost_inr=c.cost_inr,
                rosi=res.rosi,
            )
        )

    cards.sort(key=lambda card: card.rosi, reverse=True)
    return cards
