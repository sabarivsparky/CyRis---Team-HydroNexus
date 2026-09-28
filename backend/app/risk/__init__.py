"""
REAL LOGIC — Risk package init.
"""
from app.risk.agents import run_agent_debate
from app.risk.compliance import (
    generate_audit_records,
    get_compliance_mappings,
    verify_audit_record,
)
from app.risk.counterfactual import get_counterfactual_cards, run_what_if_scenario
from app.risk.engine import (
    compute_aro,
    compute_sle,
    compute_sle_components,
    get_risk_contributors,
    get_risk_summary,
    get_risk_trend,
    run_monte_carlo_simulation,
)
from app.risk.optimizer import run_submodular_optimizer

__all__ = [
    "compute_sle_components",
    "compute_sle",
    "compute_aro",
    "run_monte_carlo_simulation",
    "get_risk_summary",
    "get_risk_contributors",
    "get_risk_trend",
    "run_what_if_scenario",
    "get_counterfactual_cards",
    "run_submodular_optimizer",
    "run_agent_debate",
    "get_compliance_mappings",
    "generate_audit_records",
    "verify_audit_record",
]
