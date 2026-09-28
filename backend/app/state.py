"""
REAL LOGIC — TwinStore state manager.

Owns the live twin, bounded LRU simulation result cache, single-flight request coalescing,
and concurrency-limiting semaphores for thread-safe operation under heavy load.
"""
from __future__ import annotations

import collections
import hashlib
import json
import threading
import time

from app.config import (
    CYRIS_N_ITERATIONS,
    CYRIS_SEED,
    RESULT_CACHE_SIZE,
    SIM_CONCURRENCY,
)
from app.data.generator import generate_dataset
from app.risk.engine import run_monte_carlo_simulation
from app.schemas import Dataset, SimulationResult
from app.services.trend import TrendStore, backfill_trend
from app.twin.engine import TwinEngine


class TwinStore:
    """REAL LOGIC. Owns the live twin and caches simulation results."""

    def __init__(
        self,
        dataset: Dataset | None = None,
        seed: int = CYRIS_SEED,
        n_iterations: int = CYRIS_N_ITERATIONS,
    ):
        self.seed = seed
        self.n_iterations = n_iterations
        self._dataset = dataset or generate_dataset(seed=seed)
        self._live_twin = TwinEngine(self._dataset)

        self._lock = threading.Lock()
        self._semaphore = threading.Semaphore(SIM_CONCURRENCY)

        # LRU Cache: key -> SimulationResult
        self._cache: collections.OrderedDict[str, SimulationResult] = collections.OrderedDict()
        self._inflight: dict[str, tuple[threading.Event, dict[str, Any]]] = {}

        self.start_time = time.time()

        # Warm-up baseline run
        t0 = time.perf_counter()
        self._baseline_result = self.result_for(self._live_twin, n=self.n_iterations)
        self.baseline_runtime_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        # Trend backfill
        trend_points = backfill_trend(self._dataset, n=self.n_iterations, seed=self.seed)
        self.trend = TrendStore(trend_points)

        self._ready = True

    @property
    def is_ready(self) -> bool:
        return getattr(self, "_ready", False)

    def live_twin(self) -> TwinEngine:
        """Return reference to live twin. READ-ONLY for request handlers."""
        return self._live_twin

    def get_fingerprint(self, twin: TwinEngine) -> str:
        """Generate deterministic fingerprint for a twin graph state."""
        v_states = [(v.patch_status, round(v.exploitability, 4)) for v in twin.dataset.vulnerabilities]
        c_states = [(c.id, c.status) for c in twin.dataset.controls]
        raw = f"{len(twin.dataset.assets)}-{v_states}-{c_states}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def baseline(self) -> SimulationResult:
        """Return pre-computed baseline simulation result for live twin."""
        return self._baseline_result

    def result_for(self, twin: TwinEngine, n: int | None = None) -> SimulationResult:
        """Thread-safe, single-flight cached Monte Carlo simulation result retriever."""
        num_iter = n or self.n_iterations
        key = f"{self.get_fingerprint(twin)}:{num_iter}:{self.seed}"

        # 1. Fast Lock Check (Cache Hit)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]

            # 2. Check Single-Flight In-Flight Computation
            if key in self._inflight:
                event, box = self._inflight[key]
                # Wait outside lock for event
                waiting = True
            else:
                waiting = False
                event = threading.Event()
                box = {}
                self._inflight[key] = (event, box)

        if waiting:
            event.wait()
            if "result" in box:
                return box["result"]
            if "error" in box:
                raise box["error"]

        # 3. Compute (Single Flight Leader)
        try:
            with self._semaphore:
                res = run_monte_carlo_simulation(twin.dataset, n_iterations=num_iter, seed=self.seed)

            with self._lock:
                self._cache[key] = res
                if len(self._cache) > RESULT_CACHE_SIZE:
                    self._cache.popitem(last=False)
                box["result"] = res

            return res
        except Exception as err:
            with self._lock:
                box["error"] = err
            raise err
        finally:
            with self._lock:
                if key in self._inflight:
                    del self._inflight[key]
            event.set()
