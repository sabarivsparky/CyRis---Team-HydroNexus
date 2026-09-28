"""
REAL LOGIC — Unit tests for TrendStore and as-of replay backfill.
"""
from __future__ import annotations

import time

from app.data.generator import generate_dataset
from app.risk.engine import run_monte_carlo_simulation
from app.services.trend import TrendStore, backfill_trend


def test_trend_backfill_and_disk_cache() -> None:
    """Trend backfill computes as-of history; last point equals today's baseline EAL."""
    dataset = generate_dataset(seed=42)
    baseline_res = run_monte_carlo_simulation(dataset, n_iterations=1000, seed=42)
    expected_eal = baseline_res.org.eal_inr

    # Cold backfill
    t0 = time.perf_counter()
    points1 = backfill_trend(dataset, n=1000, seed=42)
    t_cold = (time.perf_counter() - t0) * 1000.0

    assert len(points1) > 0
    assert points1[-1].eal_inr == expected_eal

    # Cached backfill
    t1 = time.perf_counter()
    points2 = backfill_trend(dataset, n=1000, seed=42)
    t_cached = (time.perf_counter() - t1) * 1000.0

    assert len(points2) == len(points1)
    assert points2[-1].eal_inr == expected_eal
    assert t_cached < t_cold
    print(f"\nTrend Backfill Cold: {t_cold:.2f} ms | Cached: {t_cached:.2f} ms")


def test_trend_store_append() -> None:
    """TrendStore.append adds new live EAL trend points."""
    store = TrendStore([])
    assert len(store.get_points()) == 0

    store.append("2026-09-28T10:00:00Z", 31000000, label="Sep 28")
    pts = store.get_points()
    assert len(pts) == 1
    assert pts[0].eal_inr == 31000000
    assert pts[0].label == "Sep 28"
