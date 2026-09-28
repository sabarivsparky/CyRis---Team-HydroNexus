"""
REAL LOGIC — Portfolio Evaluator for Submodular Risk Optimization.

Memoized analytic EAL evaluator for subsets of options.
Evaluates portfolio subsets against cloned digital twin instances without modifying live twin state.
"""
from __future__ import annotations

import copy
import time
from typing import Any

from app.decision.evaluator import apply_mutation_to_twin
from app.decision.options import Option
from app.risk.attack_paths import analytic_eal
from app.twin.engine import TwinEngine


class PortfolioEvaluator:
    """REAL LOGIC. Memoized set-function evaluator for candidate option portfolios."""

    def __init__(self, live_twin: TwinEngine, options: list[Option]):
        self._live_twin = live_twin
        self._options_map: dict[str, Option] = {o.id: o for o in options}
        self.base_eal: float = analytic_eal(live_twin)

        # Memoization cache: frozenset(option_ids) -> analytic_eal (float)
        self._cache: dict[frozenset[str], float] = {
            frozenset(): self.base_eal
        }

        # Counters
        self.evaluations_performed: int = 0
        self.cache_hits: int = 0
        self.cumulative_seconds: float = 0.0

    def eal(self, subset: frozenset[str]) -> float:
        """Return analytic EAL for a subset of option IDs. Memoized by subset."""
        if subset in self._cache:
            self.cache_hits += 1
            return self._cache[subset]

        t0 = time.perf_counter()

        # Clone live twin
        clone = TwinEngine(copy.deepcopy(self._live_twin.dataset))

        # Apply options in canonical sorted ID order
        sorted_ids = sorted(list(subset))
        for opt_id in sorted_ids:
            if opt_id not in self._options_map:
                raise ValueError(f"Unknown option_id '{opt_id}' in portfolio subset.")
            opt = self._options_map[opt_id]
            for m in opt.mutations:
                apply_mutation_to_twin(clone, m)

        # Compute analytic EAL
        val = analytic_eal(clone)
        elapsed = time.perf_counter() - t0

        self._cache[subset] = val
        self.evaluations_performed += 1
        self.cumulative_seconds += elapsed

        return val

    def gain(self, subset: frozenset[str]) -> float:
        """Return EAL reduction (base_eal - subset_eal)."""
        return self.base_eal - self.eal(subset)

    def get_stats(self) -> dict[str, Any]:
        """Return evaluator metrics."""
        return {
            "evaluations_performed": self.evaluations_performed,
            "cache_hits": self.cache_hits,
            "cumulative_seconds": round(self.cumulative_seconds, 4),
        }
