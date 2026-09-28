"""
REAL LOGIC — Baseline measurement script for CyRIS Monte Carlo Simulation.
"""
from __future__ import annotations

import time

from app.config import DEFAULT_SEED
from app.data.generator import generate_dataset
from app.risk.engine import run_monte_carlo_simulation


def main() -> None:
    dataset = generate_dataset(seed=DEFAULT_SEED)
    start_t = time.perf_counter()
    res = run_monte_carlo_simulation(dataset, n_iterations=10_000, seed=DEFAULT_SEED)
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0

    print("=== CYRIS BASELINE SIMULATION REPORT ===")
    print(f"Dataset Assets: {len(dataset.assets)}")
    print(f"Iterations:     {res.meta.n_iterations:,}")
    print(f"Seed:           {res.meta.seed}")
    print(f"Runtime:        {elapsed_ms:.2f} ms")
    print(f"Org EAL:        INR {res.org.eal_inr:,}")
    print(f"Org VaR (95%):  INR {res.org.var95_inr:,}")
    print(f"Org VaR (99%):  INR {res.org.var99_inr:,}")
    print(f"Org CVaR (95%): INR {res.org.cvar95_inr:,}")


if __name__ == "__main__":
    main()
