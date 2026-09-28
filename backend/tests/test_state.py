"""
REAL LOGIC — Unit tests for TwinStore caching, concurrency, and single-flight behavior.
"""
from __future__ import annotations

import concurrent.futures
from unittest.mock import patch

import pytest

import app.risk.engine
from app.data.generator import generate_dataset
from app.state import TwinStore
from app.twin.engine import TwinEngine


def test_twinstore_cache_hit() -> None:
    """Cache hit returns identical simulation result object."""
    dataset = generate_dataset(seed=42)
    store = TwinStore(dataset=dataset, seed=42, n_iterations=1000)
    twin = store.live_twin()

    res1 = store.result_for(twin, n=1000)
    res2 = store.result_for(twin, n=1000)

    assert res1 is res2
    assert res1.org.eal_inr == res2.org.eal_inr


def test_twinstore_live_twin_immutability() -> None:
    """Fingerprint of live twin remains unchanged after multiple queries."""
    dataset = generate_dataset(seed=42)
    store = TwinStore(dataset=dataset, seed=42, n_iterations=1000)
    twin = store.live_twin()
    fp_before = store.get_fingerprint(twin)

    for _ in range(20):
        _ = store.result_for(twin, n=1000)

    fp_after = store.get_fingerprint(store.live_twin())
    assert fp_before == fp_after


def test_twinstore_single_flight() -> None:
    """N concurrent threads requesting the same uncached key run simulation once."""
    dataset = generate_dataset(seed=42)
    store = TwinStore(dataset=dataset, seed=42, n_iterations=1000)
    new_twin = TwinEngine(generate_dataset(seed=99))  # uncached twin

    sim_counter = 0
    orig_sim = app.risk.engine.run_monte_carlo_simulation

    def counted_sim(*args, **kwargs):
        nonlocal sim_counter
        sim_counter += 1
        return orig_sim(*args, **kwargs)

    with patch("app.state.run_monte_carlo_simulation", side_effect=counted_sim):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(store.result_for, new_twin, 1000)
                for _ in range(8)
            ]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert sim_counter == 1
    assert len(results) == 8
    first_eal = results[0].org.eal_inr
    assert all(r.org.eal_inr == first_eal for r in results)


def test_twinstore_concurrency() -> None:
    """8 parallel threads querying TwinStore yield byte-identical results."""
    dataset = generate_dataset(seed=42)
    store = TwinStore(dataset=dataset, seed=42, n_iterations=1000)
    twin = store.live_twin()

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(store.result_for, twin, 1000) for _ in range(8)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    first_eal = results[0].org.eal_inr
    assert all(r.org.eal_inr == first_eal for r in results)
