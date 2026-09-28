"""
REAL LOGIC — Integration tests for Phase 5 API endpoints (/whatif, /whatif/presets, /counterfactuals).
"""
from __future__ import annotations

import concurrent.futures
import time
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_whatif_presets_endpoint() -> None:
    """GET /api/v1/whatif/presets returns 7 predefined scenarios."""
    res = client.get("/api/v1/whatif/presets")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7
    ids = {p["id"] for p in data}
    assert "mfa_everywhere" in ids
    assert "segment_subnet_b" in ids


def test_api_whatif_endpoint_preset_and_custom() -> None:
    """POST /api/v1/whatif evaluates preset and custom mutation requests."""
    # Preset request
    t0 = time.perf_counter()
    res1 = client.post("/api/v1/whatif", json={"preset": "mfa_everywhere", "n_iterations": 2000})
    t_cold = (time.perf_counter() - t0) * 1000.0

    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["after_eal_inr"] < d1["before_eal_inr"]
    assert d1["cost_inr"] == 1_800_000

    # Cached request
    t1 = time.perf_counter()
    res2 = client.post("/api/v1/whatif", json={"preset": "mfa_everywhere", "n_iterations": 2000})
    t_cached = (time.perf_counter() - t1) * 1000.0

    assert res2.status_code == 200
    d2 = res2.json()
    assert d1["after_eal_inr"] == d2["after_eal_inr"]
    assert d1["delta_inr"] == d2["delta_inr"]
    assert d1["cost_inr"] == d2["cost_inr"]
    assert t_cached <= t_cold + 50.0
    print(f"\nPOST /whatif Cold: {t_cold:.2f} ms | Cached: {t_cached:.2f} ms")


def test_api_whatif_rejections() -> None:
    """POST /api/v1/whatif rejects invalid parameters with standard 422 / 404 envelopes."""
    # Both missing
    res_missing = client.post("/api/v1/whatif", json={})
    assert res_missing.status_code == 422
    assert res_missing.json()["error"]["code"] == "validation_error"

    # Both provided
    res_both = client.post("/api/v1/whatif", json={"preset": "mfa_everywhere", "mutations": [{"type": "delay_patch"}]})
    assert res_both.status_code == 422

    # Unknown preset
    res_unk = client.post("/api/v1/whatif", json={"preset": "unknown_preset_123"})
    assert res_unk.status_code == 404
    assert res_unk.json()["error"]["code"] == "not_found"

    # Exceeding WHATIF_MAX_MUTATIONS (10)
    too_many = [{"type": "delay_patch", "days": i} for i in range(11)]
    res_max = client.post("/api/v1/whatif", json={"mutations": too_many})
    assert res_max.status_code == 422


def test_api_counterfactuals_endpoint() -> None:
    """GET /api/v1/counterfactuals returns ranked decision cards."""
    t0 = time.perf_counter()
    res1 = client.get("/api/v1/counterfactuals?limit=6")
    t_cold = (time.perf_counter() - t0) * 1000.0

    assert res1.status_code == 200
    cards = res1.json()
    assert len(cards) > 0

    t1 = time.perf_counter()
    res2 = client.get("/api/v1/counterfactuals?limit=6")
    t_cached = (time.perf_counter() - t1) * 1000.0

    assert res1.text == res2.text
    print(f"GET /counterfactuals Cold: {t_cold:.2f} ms | Cached: {t_cached:.2f} ms")


def test_api_whatif_concurrency_single_flight() -> None:
    """6 parallel identical what-if requests return identical results."""
    payload = {"preset": "segment_subnet_b", "n_iterations": 2000}

    def make_req():
        return client.post("/api/v1/whatif", json=payload)

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(make_req) for _ in range(6)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert all(r.status_code == 200 for r in results)
    first_eal = results[0].json()["after_eal_inr"]
    assert all(r.json()["after_eal_inr"] == first_eal for r in results)
