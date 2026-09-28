"""
REAL LOGIC — Unit tests for /health endpoint and error envelope.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_response_structure() -> None:
    """GET /api/v1/health returns 200 OK with documented fields."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "ok"
    assert data["ready"] is True
    assert data["version"] == "0.1.0"
    assert data["seed"] == 42
    assert data["n_iterations"] == 10000
    assert data["twin_version"] == 1
    assert "twin_fingerprint" in data
    assert data["asset_count"] == 25
    assert data["baseline_runtime_ms"] >= 0.0
    assert data["uptime_s"] >= 0.0


def test_error_envelope_404() -> None:
    """Unknown path returns 404 with standard error envelope."""
    res = client.get("/api/v1/non_existent_route")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "not_found"


def test_cors_headers() -> None:
    """CORS preflight request returns allowed origin header."""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }
    res = client.options("/api/v1/health", headers=headers)
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
