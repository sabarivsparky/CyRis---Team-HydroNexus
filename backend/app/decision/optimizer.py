"""
REAL LOGIC — Submodular Risk Portfolio Optimizer.

The value function is the twin itself, not a formula. Overlap between controls
(e.g. MFA + PAM both dampening credential edges; micro-segmentation + zero-trust both dampening
network edges) is handled exactly because every candidate portfolio is evaluated by re-running
the twin's risk chain. This is the honest meaning of submodular optimization here.
"""
from __future__ import annotations

import copy
import time
from typing import Any

from ortools.algorithms.python import knapsack_solver

from app.config import (
    CYRIS_N_ITERATIONS,
    CYRIS_SEED,
    OPTIMIZER_EXACT_MAX_OPTIONS,
    OPTIMIZER_EXACT_TIME_BUDGET_S,
    OPTIMIZER_MAX_BUDGET_INR,
    OPTIMIZER_SWEEP_STEP_INR,
)
from app.decision.costing import compute_financial_metrics
from app.decision.evaluator import evaluate_mutations
from app.decision.options import Option, build_options
from app.decision.portfolio import PortfolioEvaluator
from app.state import TwinStore
from app.twin.engine import TwinEngine


def solve_naive_knapsack(options: list[Option], budget_inr: int) -> tuple[list[str], int]:
    """REAL LOGIC. Solve naive linear knapsack model using OR-Tools as the blueprint's foil.
    
    OR-Tools is used ONLY for the naive linear baseline; the true CyRIS optimizer
    is the twin-evaluated set-function solver.
    """
    if not options or budget_inr <= 0:
        return [], 0

    # Scale to integer units (thousands of INR)
    scale = 1_000
    capacities = [budget_inr // scale]
    values = [max(1, int(o.standalone_gain_inr // scale)) for o in options]
    weights = [[max(1, o.cost_inr // scale) for o in options]]


    if capacities[0] <= 0:
        return [], 0

    try:
        solver = knapsack_solver.KnapsackSolver(
            knapsack_solver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER,
            "NaiveKnapsackFoil",
        )
        solver.init(values, weights, capacities)
        solver.solve()
        selected_indices = [i for i in range(len(options)) if solver.best_solution_contains(i)]
        selected_ids = sorted([options[i].id for i in selected_indices])
        claimed_gain = sum(int(options[i].standalone_gain_inr) for i in selected_indices)
        return selected_ids, claimed_gain
    except Exception:
        # Fallback greedy linear knapsack if solver fails
        sorted_opts = sorted(options, key=lambda o: o.standalone_gain_inr / max(1, o.cost_inr), reverse=True)
        rem = budget_inr
        sel = []
        claimed = 0
        for opt in sorted_opts:
            if opt.cost_inr <= rem:
                sel.append(opt.id)
                rem -= opt.cost_inr
                claimed += int(opt.standalone_gain_inr)
        return sorted(sel), claimed


def enumerate_feasible_subsets(
    options: list[Option],
    max_budget_inr: int,
) -> list[tuple[int, frozenset[str]]]:
    """DFS recursion to find all subset option IDs with cost <= max_budget_inr."""
    opts = sorted(options, key=lambda o: o.cost_inr)
    results: list[tuple[int, frozenset[str]]] = []

    def dfs(idx: int, current_cost: int, current_subset: list[str]):
        results.append((current_cost, frozenset(current_subset)))
        for i in range(idx, len(opts)):
            next_opt = opts[i]
            if current_cost + next_opt.cost_inr <= max_budget_inr:
                dfs(i + 1, current_cost + next_opt.cost_inr, current_subset + [next_opt.id])

    dfs(0, 0, [])
    return results


def build_pareto_frontier(
    evaluator: PortfolioEvaluator,
    options: list[Option],
    max_budget_inr: int = OPTIMIZER_MAX_BUDGET_INR,
) -> tuple[list[dict[str, Any]], str, bool, int, float]:
    """REAL LOGIC. Build Pareto frontier over all feasible portfolios.
    
    Returns (frontier, solver_used, exact, subsets_evaluated, compute_ms).
    """
    t0 = time.perf_counter()
    n_opts = len(options)

    # Time guard projection check
    per_eval_est_s = 0.0016  # ~1.6 ms measured preflight
    feasible_count = len(enumerate_feasible_subsets(options, max_budget_inr))
    projected_time_s = feasible_count * per_eval_est_s

    use_exact = (
        n_opts <= OPTIMIZER_EXACT_MAX_OPTIONS
        and projected_time_s <= OPTIMIZER_EXACT_TIME_BUDGET_S
    )

    if use_exact:
        subsets = enumerate_feasible_subsets(options, max_budget_inr)
        evaluated_points: list[tuple[int, float, frozenset[str]]] = []
        for cost, subset in subsets:
            gain = evaluator.gain(subset)
            evaluated_points.append((cost, gain, subset))

        # Sort by cost ascending, gain descending, then lexicographical subset tuple
        evaluated_points.sort(key=lambda p: (p[0], -p[1], sorted(list(p[2]))))

        # Filter strictly monotone Pareto points
        frontier_points: list[dict[str, Any]] = []
        max_gain_so_far = -1.0

        for cost, gain, subset in evaluated_points:
            if gain > max_gain_so_far + 1e-4:
                max_gain_so_far = gain
                frontier_points.append({
                    "budget_inr": cost,
                    "cost_inr": cost,
                    "eal_reduction_inr": int(gain),
                    "option_ids": sorted(list(subset)),
                })

        compute_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        return frontier_points, "exact", True, len(subsets), compute_ms

    else:
        # Fallback: Lazy Greedy
        opts_by_cost = sorted(options, key=lambda o: o.cost_inr)
        sweep_budgets = list(range(0, max_budget_inr + 1, OPTIMIZER_SWEEP_STEP_INR))
        greedy_points: list[dict[str, Any]] = []
        eval_count = 0

        for b in sweep_budgets:
            curr_subset: set[str] = set()
            curr_cost = 0
            rem_b = b

            while True:
                best_cand = None
                best_marginal = 0.0

                for opt in opts_by_cost:
                    if opt.id in curr_subset or opt.cost_inr > rem_b:
                        continue
                    # Marginal gain per cost
                    cand_set = frozenset(curr_subset | {opt.id})
                    marginal = evaluator.gain(cand_set) - evaluator.gain(frozenset(curr_subset))
                    eval_count += 1
                    if marginal > best_marginal:
                        best_marginal = marginal
                        best_cand = opt

                if not best_cand or best_marginal <= 0:
                    break
                curr_subset.add(best_cand.id)
                curr_cost += best_cand.cost_inr
                rem_b -= best_cand.cost_inr

            # Compare with best single option
            best_single_id = None
            best_single_gain = 0.0
            for opt in opts_by_cost:
                if opt.cost_inr <= b:
                    g = evaluator.gain(frozenset([opt.id]))
                    if g > best_single_gain:
                        best_single_gain = g
                        best_single_id = opt.id

            greedy_gain = evaluator.gain(frozenset(curr_subset))
            if best_single_id and best_single_gain > greedy_gain:
                final_subset = frozenset([best_single_id])
                final_cost = evaluator._options_map[best_single_id].cost_inr
                final_gain = best_single_gain
            else:
                final_subset = frozenset(curr_subset)
                final_cost = curr_cost
                final_gain = greedy_gain

            greedy_points.append({
                "budget_inr": b,
                "cost_inr": final_cost,
                "eal_reduction_inr": int(final_gain),
                "option_ids": sorted(list(final_subset)),
            })

        # Monotone-ify greedy points
        frontier_points: list[dict[str, Any]] = []
        max_gain_so_far = -1.0
        for pt in greedy_points:
            g = float(pt["eal_reduction_inr"])
            if g > max_gain_so_far + 1e-4:
                max_gain_so_far = g
                frontier_points.append(pt)

        compute_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        return frontier_points, "lazy_greedy", False, eval_count, compute_ms


def get_best_portfolio_for_budget(
    frontier: list[dict[str, Any]],
    budget_inr: int,
) -> dict[str, Any]:
    """Find last Pareto frontier point with cost_inr <= budget_inr."""
    best = frontier[0]
    for pt in frontier:
        if pt["cost_inr"] <= budget_inr:
            best = pt
        else:
            break
    return best


def run_optimizer(store: TwinStore, budget_inr: int) -> dict[str, Any]:
    """REAL LOGIC. Compute optimal portfolio, naive baseline comparison, and MC verification."""
    if not isinstance(budget_inr, int) or budget_inr <= 0 or budget_inr > OPTIMIZER_MAX_BUDGET_INR:
        raise ValueError(f"budget_inr must be an integer between 1 and {OPTIMIZER_MAX_BUDGET_INR:,}.")

    live_twin = store.live_twin()
    options, dropped = build_options(live_twin)
    options_map = {o.id: o for o in options}

    evaluator = PortfolioEvaluator(live_twin, options)
    frontier, solver_used, exact, eval_count, compute_ms = build_pareto_frontier(evaluator, options)

    best_pt = get_best_portfolio_for_budget(frontier, budget_inr)
    selected_option_ids: list[str] = best_pt["option_ids"]
    total_cost_inr: int = best_pt["cost_inr"]
    analytic_gain_inr: int = best_pt["eal_reduction_inr"]

    # Budget below cheapest option check
    if not selected_option_ids or total_cost_inr > budget_inr:
        baseline_res = store.baseline()
        return {
            "selected_control_ids": [],
            "selected_option_ids": [],
            "selected_options": [],
            "total_cost_inr": 0,
            "retained_buffer_inr": budget_inr,
            "eal_reduction_inr": 0,
            "eal_reduction_analytic_inr": 0,
            "eal_reduction_mc_inr": 0,
            "analytic_mc_ratio": 1.0,
            "note": f"Requested budget ₹{budget_inr:,} is below the cheapest candidate option cost.",
            "mc": {
                "eal_before_inr": baseline_res.org.eal_inr,
                "eal_after_inr": baseline_res.org.eal_inr,
                "var95_before_inr": baseline_res.org.var95_inr,
                "var95_after_inr": baseline_res.org.var95_inr,
                "var99_before_inr": baseline_res.org.var99_inr,
                "var99_after_inr": baseline_res.org.var99_inr,
                "cost_inr": 0,
                "cost_breakdown": [],
                "rosi": 0.0,
                "payback_months": 0.0,
            },
            "naive_baseline": {
                "selected_option_ids": [],
                "claimed_reduction_inr": 0,
                "true_reduction_inr": 0,
                "overstatement_ratio": None,
                "cyris_advantage_inr": 0,
            },
            "marginal_values": {},
            "overlap_discount_inr": 0,
            "solver_used": solver_used,
            "exact": exact,
            "twin_fingerprint": store.get_fingerprint(live_twin),
        }

    # Extract controls vs all options
    selected_controls = [o for o in options if o.id in selected_option_ids and o.kind == "control"]
    selected_control_ids = [c.id for c in selected_controls]
    selected_options_payload = [options_map[oid].model_dump() for oid in selected_option_ids]

    # Combine all mutations
    combined_mutations: list[dict[str, Any]] = []
    for oid in selected_option_ids:
        combined_mutations.extend(options_map[oid].mutations)

    # Full Monte Carlo simulation via evaluate_mutations (CRN seed 42)
    mc_eval = evaluate_mutations(store, mutations=combined_mutations, n=CYRIS_N_ITERATIONS)
    mc_gain_inr = int(mc_eval["delta_inr"] * -1)  # delta_inr is negative for reduction

    analytic_mc_ratio = round(analytic_gain_inr / max(1, mc_gain_inr), 4)

    # Naive knapsack foil comparison
    naive_ids, naive_claimed = solve_naive_knapsack(options, budget_inr)
    if naive_ids:
        naive_true = int(evaluator.gain(frozenset(naive_ids)))
        overstatement_ratio = round(naive_claimed / naive_true, 4) if naive_true > 0 else None
    else:
        naive_true = 0
        overstatement_ratio = None

    cyris_advantage_inr = max(0, analytic_gain_inr - naive_true)

    # Marginal values & overlap discount
    S = frozenset(selected_option_ids)
    marginal_values: dict[str, int] = {}
    sum_standalone = 0
    for oid in selected_option_ids:
        S_minus = S - {oid}
        m_val = int(evaluator.gain(S) - evaluator.gain(S_minus))
        marginal_values[oid] = m_val
        sum_standalone += int(options_map[oid].standalone_gain_inr)

    overlap_discount_inr = sum_standalone - analytic_gain_inr

    # Sweep curve points
    sweep_budgets = list(range(0, OPTIMIZER_MAX_BUDGET_INR + 1, OPTIMIZER_SWEEP_STEP_INR))
    curve: list[dict[str, Any]] = []
    for b in sweep_budgets:
        pt = get_best_portfolio_for_budget(frontier, b)
        cost = pt["cost_inr"]
        gain = pt["eal_reduction_inr"]
        rosi_val = round((gain - cost) / cost, 2) if cost > 0 else 0.0
        curve.append({
            "budget_inr": b,
            "cost_inr": cost,
            "eal_reduction_inr": gain,
            "rosi": rosi_val,
            "option_ids": pt["option_ids"],
        })

    return {
        "selected_control_ids": selected_control_ids,
        "selected_option_ids": selected_option_ids,
        "selected_options": selected_options_payload,
        "total_cost_inr": total_cost_inr,
        "retained_buffer_inr": budget_inr - total_cost_inr,
        "eal_reduction_inr": mc_gain_inr,
        "eal_reduction_analytic_inr": analytic_gain_inr,
        "eal_reduction_mc_inr": mc_gain_inr,
        "analytic_mc_ratio": analytic_mc_ratio,
        "mc": {
            "eal_before_inr": mc_eval["before_eal_inr"],
            "eal_after_inr": mc_eval["after_eal_inr"],
            "var95_before_inr": mc_eval["var95_before_inr"],
            "var95_after_inr": mc_eval["var95_after_inr"],
            "var99_before_inr": mc_eval["var99_before_inr"],
            "var99_after_inr": mc_eval["var99_after_inr"],
            "cost_inr": mc_eval["cost_inr"],
            "cost_breakdown": mc_eval["cost_breakdown"],
            "rosi": mc_eval["rosi"],
            "payback_months": mc_eval["payback_months"],
        },
        "naive_baseline": {
            "selected_option_ids": naive_ids,
            "claimed_reduction_inr": naive_claimed,
            "true_reduction_inr": naive_true,
            "overstatement_ratio": overstatement_ratio,
            "cyris_advantage_inr": cyris_advantage_inr,
        },
        "marginal_values": marginal_values,
        "overlap_discount_inr": overlap_discount_inr,
        "curve": curve,
        "solver_used": solver_used,
        "exact": exact,
        "twin_fingerprint": store.get_fingerprint(live_twin),
    }
