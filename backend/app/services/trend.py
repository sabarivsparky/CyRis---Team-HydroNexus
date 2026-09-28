"""
REAL LOGIC — Trend Computation over Simulated History.

Computes historical EAL trend points via honest as-of replay (filtering vulnerabilities
by discovered_date) and caches computed series to disk.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from app.config import (
    AS_OF_DATE_ISO,
    TREND_BACKFILL_DAYS,
    TREND_BACKFILL_STEP_DAYS,
)
from app.risk.engine import run_monte_carlo_simulation
from app.schemas import Dataset, TrendPoint

TREND_CACHE_PATH = Path(__file__).parent.parent.parent / "data" / "generated" / "trend_cache.json"


class TrendStore:
    """Stores historical and live EAL trend points."""

    def __init__(self, points: list[TrendPoint] | None = None):
        self._points: list[TrendPoint] = points or []

    def get_points(self) -> list[TrendPoint]:
        return list(self._points)

    def append(self, timestamp: str, eal_inr: int, label: str = "") -> None:
        """Append a new live EAL trend point."""
        lbl = label or timestamp[:10]
        self._points.append(
            TrendPoint(
                label=lbl,
                eal=eal_inr,
                timestamp=timestamp,
                eal_inr=eal_inr,
            )
        )


def _compute_dataset_key(dataset: Dataset, n: int, seed: int) -> str:
    """Compute unique cache key for dataset state, n_iterations, and seed."""
    raw = f"{len(dataset.assets)}-{len(dataset.vulnerabilities)}-{n}-{seed}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def backfill_trend(dataset: Dataset, n: int, seed: int) -> list[TrendPoint]:
    """Replay dataset state over TREND_BACKFILL_DAYS and compute EAL history."""
    cache_key = _compute_dataset_key(dataset, n, seed)

    # Check disk cache
    if TREND_CACHE_PATH.exists():
        try:
            with open(TREND_CACHE_PATH, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                if cached_data.get("cache_key") == cache_key and "points" in cached_data:
                    return [TrendPoint.model_validate(p) for p in cached_data["points"]]
        except Exception:
            pass

    today = datetime.date.fromisoformat(AS_OF_DATE_ISO)
    points: list[TrendPoint] = []
    days_to_replay = list(range(TREND_BACKFILL_DAYS - 1, -1, -TREND_BACKFILL_STEP_DAYS))
    if 0 not in days_to_replay:
        days_to_replay.append(0)
    days_to_replay.sort(reverse=True)

    for d in days_to_replay:
        as_of_d = today - datetime.timedelta(days=d)
        ds_d = copy.deepcopy(dataset)
        ds_d.as_of = as_of_d
        ds_d.vulnerabilities = [v for v in ds_d.vulnerabilities if v.discovered_date <= as_of_d]

        sim_res = run_monte_carlo_simulation(ds_d, n_iterations=n, seed=seed)
        eal_d = sim_res.org.eal_inr

        lbl = as_of_d.strftime("%b %d")
        points.append(
            TrendPoint(
                label=lbl,
                eal=eal_d,
                timestamp=f"{as_of_d.isoformat()}T00:00:00Z",
                eal_inr=eal_d,
            )
        )

    # Save to disk cache
    TREND_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cache_payload = {
        "cache_key": cache_key,
        "points": [p.model_dump(mode="json") for p in points],
    }
    with open(TREND_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache_payload, f, indent=2)

    return points
