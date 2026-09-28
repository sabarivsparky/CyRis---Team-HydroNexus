"""
REAL LOGIC — Integration tests for Phase 3 endpoints (/health, /risk/summary, /risk/contributors, /risk/trend).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_health_endpoint() -> None:
    """GET /api/v1/health returns 200 OK with health details."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["ready"] is True
    assert data["version"] == "0.1.0"


def test_api_risk_summary_endpoint() -> None:
    """GET /api/v1/risk/summary returns 200 OK with risk metrics."""
    response = client.get("/api/v1/risk/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["eal_inr"] > 0
    assert data["var95_inr"] >= data["eal_inr"]
    assert len(data["histogram"]) == 50
    assert len(data["exceedance_curve"]) == 40


def test_api_risk_contributors_endpoint() -> None:
    """GET /api/v1/risk/contributors with query param level."""
    for lvl in ["asset", "vulnerability", "business_unit"]:
        response = client.get(f"/api/v1/risk/contributors?level={lvl}&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


def test_api_risk_trend_endpoint() -> None:
    """GET /api/v1/risk/trend returns 200 OK with trend points."""
    response = client.get("/api/v1/risk/trend")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
