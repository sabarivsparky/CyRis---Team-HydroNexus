"""
REAL LOGIC — Unit tests for /risk API endpoints.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.data.generator import generate_dataset
from app.main import app
from app.risk.engine import run_monte_carlo_simulation
from app.schemas import RiskContributor, RiskSummary, TrendPoint

client = TestClient(app)


def test_risk_summary_endpoint() -> None:
    """GET /risk/summary returns RiskSummary matching baseline exactly."""
    res1 = client.get("/api/v1/risk/summary")
    assert res1.status_code == 200
    data1 = res1.json()

    # Determinism
    res2 = client.get("/api/v1/risk/summary")
    assert res1.text == res2.text

    summary = RiskSummary.model_validate(data1)
    assert summary.eal_inr > 0
    assert summary.var95_inr >= summary.eal_inr

    # Compare against direct Monte Carlo run
    ds = generate_dataset(seed=42)
    direct_res = run_monte_carlo_simulation(ds, n_iterations=10000, seed=42)
    assert summary.eal_inr == direct_res.org.eal_inr


def test_risk_contributors_endpoint() -> None:
    """GET /risk/contributors validates sorting, limits, level filtering, and errors."""
    # Test levels
    for lvl in ["asset", "vulnerability", "business_unit"]:
        res = client.get(f"/api/v1/risk/contributors?level={lvl}&limit=5")
        assert res.status_code == 200
        items = [RiskContributor.model_validate(i) for i in res.json()]
        assert len(items) <= 5

        # Check desc sorting
        eals = [i.eal_inr for i in items]
        assert eals == sorted(eals, reverse=True)

        # Shares in [0, 1]
        for i in items:
            assert 0.0 <= i.share_ratio <= 1.0

    # Vulnerability level covers vulnerabilities from > 1 asset
    v_res = client.get("/api/v1/risk/contributors?level=vulnerability&limit=50")
    assert v_res.status_code == 200
    v_items = [RiskContributor.model_validate(i) for i in v_res.json()]
    assert len(v_items) > 1

    # Invalid level -> 422
    err_res = client.get("/api/v1/risk/contributors?level=invalid_level")
    assert err_res.status_code == 422
    err_data = err_res.json()
    assert err_data["error"]["code"] == "validation_error"


def test_risk_trend_endpoint() -> None:
    """GET /risk/trend returns trend points where last point equals baseline EAL."""
    res = client.get("/api/v1/risk/trend")
    assert res.status_code == 200
    points = [TrendPoint.model_validate(p) for p in res.json()]
    assert len(points) > 0

    # Last point equals baseline EAL
    summary_res = client.get("/api/v1/risk/summary")
    baseline_eal = summary_res.json()["eal_inr"]
    assert points[-1].eal_inr == baseline_eal
