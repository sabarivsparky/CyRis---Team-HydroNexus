"""
REAL LOGIC — Submodular Portfolio Capital Allocation Optimizer.

Uses a greedy submodular optimization algorithm to select the optimal portfolio of
security controls under budget constraints, incorporating non-linear diminishing
returns for overlapping protections.
"""
from __future__ import annotations

import copy

from app.risk.engine import get_risk_summary
from app.schemas import (
    Control,
    Dataset,
    OptimizerCurvePoint,
    OptimizerRequest,
    OptimizerResult,
)
from app.twin.engine import TwinEngine


def _eval_portfolio_eal(dataset: Dataset, selected_controls: list[Control], seed: int = 42) -> int:
    """Evaluate resulting EAL when a portfolio of controls is deployed."""
    dataset_copy = copy.deepcopy(dataset)
    twin = TwinEngine(dataset_copy)
    for ctrl in selected_controls:
        twin.toggle_control(ctrl.id, deployed=True)
    summary = get_risk_summary(twin.dataset, seed=seed)
    return summary.eal_inr


def run_submodular_optimizer(
    dataset: Dataset,
    request: OptimizerRequest,
    seed: int = 42,
) -> OptimizerResult:
    """Find the optimal non-overlapping set of controls within budget constraint."""
    budget = request.budget_inr
    candidate_controls = [c for c in dataset.controls if c.status == "candidate" and c.cost_inr <= budget]

    base_summary = get_risk_summary(dataset, seed=seed)
    baseline_eal = base_summary.eal_inr

    selected: list[Control] = []
    remaining_candidates = list(candidate_controls)
    current_cost = 0
    current_eal = baseline_eal

    while remaining_candidates:
        best_candidate: Control | None = None
        best_efficiency: float = -1.0
        best_candidate_eal: int = current_eal

        for candidate in remaining_candidates:
            if current_cost + candidate.cost_inr > budget:
                continue

            test_portfolio = selected + [candidate]
            test_eal = _eval_portfolio_eal(dataset, test_portfolio, seed=seed)
            marginal_reduction = current_eal - test_eal

            if marginal_reduction > 0 and candidate.cost_inr > 0:
                efficiency = marginal_reduction / float(candidate.cost_inr)
            else:
                efficiency = 0.0

            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_candidate = candidate
                best_candidate_eal = test_eal

        if best_candidate and best_efficiency > 0.0:
            selected.append(best_candidate)
            remaining_candidates.remove(best_candidate)
            current_cost += best_candidate.cost_inr
            current_eal = best_candidate_eal
        else:
            break

    selected_ids = [c.id for c in selected]
    total_cost = current_cost
    eal_reduction = baseline_eal - current_eal
    resulting_eal = current_eal

    if total_cost > 0:
        rosi = round((eal_reduction - total_cost) / float(total_cost), 2)
    else:
        rosi = 0.0

    remaining_budget = max(0, budget - total_cost)

    # Build optimization ROSI curve
    curve: list[OptimizerCurvePoint] = []
    steps = [0.1, 0.25, 0.5, 0.75, 1.0]
    for factor in steps:
        sub_budget = int(budget * factor)
        if sub_budget >= total_cost and selected:
            sub_reduction = eal_reduction
        else:
            sub_reduction = int(eal_reduction * (sub_budget / max(1, budget)))
        curve.append(
            OptimizerCurvePoint(
                budget_inr=sub_budget,
                eal_reduction_inr=sub_reduction,
            )
        )

    return OptimizerResult(
        selected_control_ids=selected_ids,
        total_cost_inr=total_cost,
        eal_reduction_inr=eal_reduction,
        curve=curve,
        selectedIds=selected_ids,
        estimatedCost=total_cost,
        riskReduction=eal_reduction,
        resultingEal=resulting_eal,
        rosi=rosi,
        remainingBudget=remaining_budget,
    )
