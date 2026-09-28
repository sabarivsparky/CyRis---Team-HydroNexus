"""
REAL LOGIC — Integration tests for Phase 6 Budget Optimizer API endpoints (app.api.routes_optimizer).
"""
import pytest
from fastapi.testclient import TestClient

from app.config import API_PREFIX, OPTIMIZER_MAX_BUDGET_INR
from app.main import app

client = TestClient(app)


def test_optimizer_options_endpoint():
    """Verify GET /api/v1/optimizer/options structure."""
    res = client.get(f"{API_PREFIX}/optimizer/options")
    assert res.status_code == 200
    data = res.json()

    assert "options" in data
    assert "dropped" in data
    assert "twin_fingerprint" in data
    assert len(data["options"]) > 0


def test_optimizer_frontier_endpoint():
    """Verify GET /api/v1/optimizer/frontier structure and metadata."""
    res = client.get(f"{API_PREFIX}/optimizer/frontier")
    assert res.status_code == 200
    data = res.json()

    assert "frontier" in data
    assert "options" in data
    assert "baseline_eal_inr" in data
    assert "meta" in data

    meta = data["meta"]
    assert meta["solver_used"] in ("exact", "lazy_greedy")
    assert isinstance(meta["exact"], bool)
    assert meta["subsets_evaluated"] > 0
    assert meta["compute_ms"] >= 0.0

    frontier = data["frontier"]
    assert len(frontier) > 0
    # Costs and gains strictly increasing along frontier
    for p1, p2 in zip(frontier[:-1], frontier[1:]):
        assert p1["cost_inr"] <= p2["cost_inr"]
        assert p1["eal_reduction_inr"] < p2["eal_reduction_inr"]


def test_optimizer_run_endpoint_valid():
    """Verify POST /api/v1/optimizer/run execution for valid budget."""
    payload = {"budget_inr": 3_000_000}
    res = client.post(f"{API_PREFIX}/optimizer/run", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Core financial & optimizer fields
    assert "selected_control_ids" in data
    assert "selected_option_ids" in data
    assert "selected_options" in data
    assert "total_cost_inr" in data
    assert data["total_cost_inr"] <= 3_000_000
    assert data["retained_buffer_inr"] == 3_000_000 - data["total_cost_inr"]

    # Monte Carlo verification payload
    assert "mc" in data
    mc = data["mc"]
    assert mc["eal_after_inr"] < mc["eal_before_inr"]
    assert mc["var95_after_inr"] <= mc["var95_before_inr"]
    assert mc["cost_inr"] == data["total_cost_inr"]

    # Naive knapsack comparison
    assert "naive_baseline" in data
    naive = data["naive_baseline"]
    assert "claimed_reduction_inr" in naive
    assert "true_reduction_inr" in naive
    assert "cyris_advantage_inr" in naive

    # Marginal values & curve
    assert "marginal_values" in data
    assert "overlap_discount_inr" in data
    assert "curve" in data
    assert len(data["curve"]) > 0


def test_optimizer_run_endpoint_rejections():
    """Verify 422 HTTP rejections for invalid budget inputs."""
    invalid_inputs = [
        {"budget_inr": 0},
        {"budget_inr": -500_000},
        {"budget_inr": OPTIMIZER_MAX_BUDGET_INR + 1_000_000},
        {"budget_inr": 2_500_000.50},  # non-integer
        {"budget_inr": "5000000"},     # string
        {},                            # missing
    ]

    for body in invalid_inputs:
        res = client.post(f"{API_PREFIX}/optimizer/run", json=body)
        assert res.status_code == 422, f"Failed to reject invalid body {body}"
        err_data = res.json()
        assert "detail" in err_data or "message" in err_data


def test_optimizer_run_tiny_budget():
    """Verify 200 response with empty portfolio note when budget is below cheapest option."""
    payload = {"budget_inr": 10_000}  # ₹10k < ₹40k minimum option
    res = client.post(f"{API_PREFIX}/optimizer/run", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["selected_option_ids"] == []
    assert data["total_cost_inr"] == 0
    assert data["retained_buffer_inr"] == 10_000
    assert "note" in data
    assert "cheapest" in data["note"]


def test_client_side_equivalence():
    """Verify client-side largest cost <= budget lookup matches server portfolio for 20 budgets."""
    frontier_res = client.get(f"{API_PREFIX}/optimizer/frontier")
    assert frontier_res.status_code == 200
    frontier = frontier_res.json()["frontier"]

    test_budgets = [
        100_000, 250_000, 500_000, 750_000, 1_000_000, 1_500_000, 2_000_000,
        2_500_000, 3_000_000, 3_500_000, 4_000_000, 4_500_000, 5_000_000,
        6_000_000, 7_000_000, 8_000_000, 9_000_000, 10_000_000
    ]

    for b in test_budgets:
        # Client-side lookup: largest cost_inr <= budget
        best_client = frontier[0]
        for pt in frontier:
            if pt["cost_inr"] <= b:
                best_client = pt
            else:
                break

        run_res = client.post(f"{API_PREFIX}/optimizer/run", json={"budget_inr": b})
        assert run_res.status_code == 200
        run_data = run_res.json()

        assert run_data["selected_option_ids"] == best_client["option_ids"]
        assert run_data["total_cost_inr"] == best_client["cost_inr"]
