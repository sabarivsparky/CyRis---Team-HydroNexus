"""
REAL LOGIC — Integration tests for Phase 4 API endpoints (/twin/graph, /attack-paths, /attack-paths/chokepoints, /assets/{id}).
"""
from __future__ import annotations

import time
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_twin_graph_endpoint() -> None:
    """GET /api/v1/twin/graph returns 200 OK with enriched nodes & edges."""
    t0 = time.perf_counter()
    res = client.get("/api/v1/twin/graph?include_controls=true")
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"\nGET /twin/graph latency: {elapsed_ms:.2f} ms")

    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) >= 26
    assert len(data["edges"]) >= 7

    # Assert no protects edge is marked as attack edge
    for e in data["edges"]:
        if e.get("kind") == "attack":
            assert e.get("protects") is not True


def test_api_attack_paths_endpoint() -> None:
    """GET /api/v1/attack-paths returns 200 OK with ranked paths."""
    t0 = time.perf_counter()
    res = client.get("/api/v1/attack-paths?k=3")
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"GET /attack-paths latency: {elapsed_ms:.2f} ms")

    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert data[0]["path_probability"] > 0.0


def test_api_chokepoints_endpoint() -> None:
    """GET /api/v1/attack-paths/chokepoints returns 200 OK with recommendations."""
    t0 = time.perf_counter()
    res = client.get("/api/v1/attack-paths/chokepoints?limit=5")
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    print(f"GET /attack-paths/chokepoints latency: {elapsed_ms:.2f} ms")

    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert data[0]["eal_drop_inr"] >= 0


def test_api_asset_detail_endpoint() -> None:
    """GET /api/v1/assets/{asset_id} returns 200 OK for valid asset, 404 for invalid."""
    res = client.get("/api/v1/assets/AST-001")
    assert res.status_code == 200
    data = res.json()
    assert data["asset"]["id"] == "AST-001"
    assert "vulnerabilities" in data
    assert "controls" in data
    assert "path_from_internet" in data

    # Unknown asset -> 404
    err_res = client.get("/api/v1/assets/NON_EXISTENT")
    assert err_res.status_code == 404
    assert err_res.json()["error"]["code"] == "not_found"
