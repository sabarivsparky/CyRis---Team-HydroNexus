"""
REAL LOGIC — Services package init.
"""
from app.services.trend import TrendStore, backfill_trend

__all__ = ["TrendStore", "backfill_trend"]
