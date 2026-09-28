"""
REAL LOGIC — Decision & Counterfactual Package init.
"""
from app.decision.counterfactuals import generate_counterfactual_cards
from app.decision.evaluator import evaluate_mutations
from app.decision.presets import get_all_presets, get_preset

__all__ = [
    "evaluate_mutations",
    "generate_counterfactual_cards",
    "get_all_presets",
    "get_preset",
]
