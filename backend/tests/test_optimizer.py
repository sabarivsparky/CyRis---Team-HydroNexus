"""
REAL LOGIC — Unit tests for Portfolio Evaluator, Solvers, and Submodularity (app.decision.optimizer).
"""
import itertools
import random
import pytest

from app.config import OPTIMIZER_MAX_BUDGET_INR, OPTIMIZER_SWEEP_STEP_INR
from app.decision.options import build_options
from app.decision.optimizer import (
    build_pareto_frontier,
    enumerate_feasible_subsets,
    get_best_portfolio_for_budget,
    solve_naive_knapsack,
)
from app.decision.portfolio import PortfolioEvaluator
from app.risk.attack_paths import analytic_eal
from app.state import TwinStore


def test_evaluator_properties_and_memoization():
    """Verify evaluator monotonicity, memoization hits, and live twin state preservation."""
    store = TwinStore()
    live_twin = store.live_twin()
    fp_before = store.get_fingerprint(live_twin)

    options, _ = build_options(live_twin)
    evaluator = PortfolioEvaluator(live_twin, options)

    # eal(∅) == base_eal
    base_eal = evaluator.eal(frozenset())
    assert base_eal == analytic_eal(live_twin)

    # Monotonicity test: adding options never increases EAL
    single_gains = []
    for opt in options:
        sub = frozenset([opt.id])
        opt_eal = evaluator.eal(sub)
        assert opt_eal <= base_eal + 1e-4, f"Option {opt.id} increased EAL!"
        single_gains.append(evaluator.gain(sub))

    # Memoization hit test
    hits_before = evaluator.cache_hits
    evaluator.eal(frozenset([options[0].id]))
    assert evaluator.cache_hits == hits_before + 1

    # Live twin fingerprint unchanged
    fp_after = store.get_fingerprint(live_twin)
    assert fp_before == fp_after, "Live twin must remain unmutated!"


def test_independent_brute_force_oracle():
    """Independent oracle test comparing DFS solver against brute-force itertools combinations."""
    store = TwinStore()
    live_twin = store.live_twin()
    options, _ = build_options(live_twin)

    # Take a small sub-catalog of 6 options for oracle verification
    small_opts = options[:6]
    evaluator = PortfolioEvaluator(live_twin, small_opts)

    oracle_max_budget = 3_000_000
    all_subsets = []
    for k in range(len(small_opts) + 1):
        for combo in itertools.combinations(small_opts, k):
            cost = sum(o.cost_inr for o in combo)
            if cost <= oracle_max_budget:
                c_ids = frozenset(o.id for o in combo)
                gain = evaluator.gain(c_ids)
                all_subsets.append((cost, gain, sorted(list(c_ids))))

    # Grid check over fine budget steps
    frontier, _, _, _, _ = build_pareto_frontier(evaluator, small_opts, max_budget_inr=oracle_max_budget)

    for budget in range(0, oracle_max_budget + 1, 250_000):
        # Best via oracle
        feasible_oracle = [s for s in all_subsets if s[0] <= budget]
        feasible_oracle.sort(key=lambda s: (s[1], -s[0]), reverse=True)
        oracle_best = feasible_oracle[0] if feasible_oracle else (0, 0.0, [])

        # Best via solver
        solver_best = get_best_portfolio_for_budget(frontier, budget)

        assert solver_best["cost_inr"] <= budget
        assert abs(solver_best["eal_reduction_inr"] - int(oracle_best[1])) <= 1, (
            f"Mismatch at budget {budget}: solver gain {solver_best['eal_reduction_inr']} != oracle {oracle_best[1]}"
        )


def test_submodularity_sampling_rate():
    """Sample >= 300 random (A ⊆ B, x ∉ B) triples to test submodularity / diminishing returns."""
    store = TwinStore()
    live_twin = store.live_twin()
    options, _ = build_options(live_twin)
    evaluator = PortfolioEvaluator(live_twin, options)

    all_ids = [o.id for o in options]
    rng = random.Random(42)

    sample_size = 350
    satisfied_count = 0
    eps = 1e-4
    violations = []

    for _ in range(sample_size):
        # Pick x
        x = rng.choice(all_ids)
        rem = [i for i in all_ids if i != x]

        # Pick size of B (at least 1) and size of A
        size_b = rng.randint(1, len(rem))
        set_b = set(rng.sample(rem, size_b))
        size_a = rng.randint(0, len(set_b))
        set_a = set(rng.sample(list(set_b), size_a))

        A = frozenset(set_a)
        B = frozenset(set_b)

        gain_a_x = evaluator.gain(A | {x}) - evaluator.gain(A)
        gain_b_x = evaluator.gain(B | {x}) - evaluator.gain(B)

        if gain_a_x >= gain_b_x - eps:
            satisfied_count += 1
        else:
            violations.append((sorted(list(A)), sorted(list(B)), x, gain_a_x, gain_b_x))

    rate = (satisfied_count / sample_size) * 100.0
    print(f"\nSubmodularity diminishing returns rate: {rate:.2f}% ({satisfied_count}/{sample_size})")

    # Assert submodularity monotonicity / high satisfaction rate
    assert rate >= 80.0, f"Submodularity rate too low: {rate:.2f}%"


def test_naive_vs_cyris_comparison():
    """Compare naive linear knapsack solver against exact CyRIS submodular optimizer."""
    store = TwinStore()
    live_twin = store.live_twin()
    options, _ = build_options(live_twin)
    evaluator = PortfolioEvaluator(live_twin, options)

    frontier, _, _, _, _ = build_pareto_frontier(evaluator, options)
    sweep_budgets = list(range(500_000, OPTIMIZER_MAX_BUDGET_INR + 1, OPTIMIZER_SWEEP_STEP_INR))

    overstatement_count = 0
    diff_count = 0

    for b in sweep_budgets:
        cyris_best = get_best_portfolio_for_budget(frontier, b)
        cyris_true = cyris_best["eal_reduction_inr"]

        naive_ids, naive_claimed = solve_naive_knapsack(options, b)
        naive_true = int(evaluator.gain(frozenset(naive_ids)))

        # 1. Exact solver guarantee: CyRIS true >= Naive true
        assert cyris_true >= naive_true - 1

        # 2. Claimed vs True for linear model
        assert naive_claimed >= naive_true - 1

        if naive_ids != cyris_best["option_ids"]:
            diff_count += 1
        if naive_claimed > naive_true:
            overstatement_count += 1

    print(f"\nNaive vs CyRIS: Differed at {diff_count}/{len(sweep_budgets)} budgets. "
          f"Linear model overstated gain at {overstatement_count}/{len(sweep_budgets)} budgets.")


def test_greedy_fallback_and_time_guard(monkeypatch):
    """Verify lazy-greedy fallback solver performance and time guard path."""
    store = TwinStore()
    live_twin = store.live_twin()
    options, _ = build_options(live_twin)
    evaluator = PortfolioEvaluator(live_twin, options)

    # Exact frontier
    exact_frontier, exact_solver, exact_is_exact, _, _ = build_pareto_frontier(evaluator, options)
    assert exact_solver == "exact"
    assert exact_is_exact is True

    # Force fallback by monkeypatching OPTIMIZER_EXACT_MAX_OPTIONS
    import app.decision.optimizer as opt_mod
    monkeypatch.setattr(opt_mod, "OPTIMIZER_EXACT_MAX_OPTIONS", 2)

    greedy_frontier, greedy_solver, greedy_is_exact, _, _ = build_pareto_frontier(evaluator, options)
    assert greedy_solver == "lazy_greedy"
    assert greedy_is_exact is False

    # Compare greedy gain vs exact gain across sweep budgets (must be >= 80% ratio)
    sweep_budgets = list(range(1_000_000, OPTIMIZER_MAX_BUDGET_INR + 1, OPTIMIZER_SWEEP_STEP_INR))
    ratios = []

    for b in sweep_budgets:
        exact_pt = get_best_portfolio_for_budget(exact_frontier, b)
        greedy_pt = get_best_portfolio_for_budget(greedy_frontier, b)

        e_gain = max(1, exact_pt["eal_reduction_inr"])
        g_gain = greedy_pt["eal_reduction_inr"]
        ratio = g_gain / e_gain
        ratios.append(ratio)

        assert ratio >= 0.80, f"Greedy ratio too low at budget {b}: {ratio:.2f}"

    avg_ratio = sum(ratios) / len(ratios)
    print(f"\nGreedy vs Exact average performance ratio: {avg_ratio*100.0:.2f}%")
