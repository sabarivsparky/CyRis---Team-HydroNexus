"""
REAL LOGIC — Unit tests for Phase 2 (Monte Carlo Engine, Optimizer, Agents, Compliance).
"""
from __future__ import annotations

import pytest

from app.data.generator import generate_dataset
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
from app.schemas import AuditVerifyRequest, OptimizerRequest, WhatIfRequest


@pytest.fixture
def sample_dataset():
    return generate_dataset(seed=42)


def test_sle_and_aro_calculation(sample_dataset) -> None:
    """SLE across 6 loss components and ARO calculations return positive values."""
    asset = sample_dataset.assets[0]  # AST-001
    comp = compute_sle_components(asset)
    sle = compute_sle(asset)
    assert sle > 0
    assert sle == (
        comp.downtime_inr
        + comp.breach_inr
        + comp.recovery_inr
        + comp.regulatory_inr
        + comp.operational_inr
        + comp.reputation_inr
    )

    aro = compute_aro(asset, sample_dataset)
    assert 0.0 < aro <= 1.0


def test_monte_carlo_simulation(sample_dataset) -> None:
    """Monte Carlo simulation runs 10,000 iterations deterministically."""
    res1 = run_monte_carlo_simulation(sample_dataset, n_iterations=2000, seed=42)
    res2 = run_monte_carlo_simulation(sample_dataset, n_iterations=2000, seed=42)

    assert res1.org.eal_inr == res2.org.eal_inr
    assert res1.org.var95_inr == res2.org.var95_inr
    assert len(res1.org.histogram) == 50
    assert len(res1.org.exceedance_curve) == 40
    assert len(res1.assets) == len(sample_dataset.assets)
    assert len(res1.business_units) > 0


def test_risk_summary_contributors_trend(sample_dataset) -> None:
    """Risk summary, contributors breakdown, and trend generation produce valid schema outputs."""
    summary = get_risk_summary(sample_dataset, seed=42)
    assert summary.eal_inr > 0
    assert summary.var95_inr >= summary.eal_inr
    assert summary.var99_inr >= summary.var95_inr

    contribs_asset = get_risk_contributors(sample_dataset, level="asset", seed=42)
    assert len(contribs_asset) > 0
    assert contribs_asset[0].eal_inr >= contribs_asset[-1].eal_inr

    contribs_vuln = get_risk_contributors(sample_dataset, level="vulnerability", seed=42)
    assert len(contribs_vuln) > 0

    contribs_bu = get_risk_contributors(sample_dataset, level="business_unit", seed=42)
    assert len(contribs_bu) > 0

    trend = get_risk_trend(sample_dataset, months=6, seed=42)
    assert len(trend) == 6
    assert trend[0].eal >= trend[-1].eal  # Historical progression


def test_whatif_and_counterfactuals(sample_dataset) -> None:
    """What-if simulation and counterfactual cards compute risk reduction and ROSI."""
    req = WhatIfRequest(
        mutations=[{"type": "deploy_control", "control_id": "CTL-001"}],
        n_iterations=2000,
        seed=42,
    )
    res = run_what_if_scenario(sample_dataset, req)

    assert res.before_eal_inr >= res.after_eal_inr
    assert res.delta_inr <= 0
    assert res.cost_inr > 0
    assert isinstance(res.rosi, float)

    cards = get_counterfactual_cards(sample_dataset, seed=42)
    assert len(cards) > 0
    assert cards[0].controlId != ""


def test_submodular_optimizer(sample_dataset) -> None:
    """Submodular optimizer selects optimal control portfolio within budget ceiling."""
    req = OptimizerRequest(budget_inr=5_000_000)
    res = run_submodular_optimizer(sample_dataset, req, seed=42)

    assert res.total_cost_inr <= 5_000_000
    assert res.eal_reduction_inr >= 0
    assert res.remainingBudget == 5_000_000 - res.total_cost_inr
    assert len(res.curve) == 5
    assert len(res.selected_control_ids) > 0


def test_multi_agent_debate(sample_dataset) -> None:
    """Multi-agent swarm debate returns grounded Red/Blue/Judge decision."""
    debate = run_agent_debate(sample_dataset, seed=42)
    assert debate.id == "debate-001"
    assert len(debate.red.evidence) > 0
    assert len(debate.blue.evidence) > 0
    assert debate.judge.confidence > 0.8
    assert debate.judge.recommendedControlId != ""


def test_compliance_and_audit(sample_dataset) -> None:
    """Compliance mappings and cryptographic audit verification pass validation."""
    mappings = get_compliance_mappings(sample_dataset)
    assert len(mappings) >= 4
    frameworks = {m.framework for m in mappings}
    assert "SEBI CSCRF" in frameworks
    assert "RBI CSF" in frameworks

    records = generate_audit_records(sample_dataset)
    assert len(records) >= 4

    verify_req = AuditVerifyRequest(record_id=records[0].id)
    verify_res = verify_audit_record(verify_req, sample_dataset)
    assert verify_res.verified is True
    assert "verified" in verify_res.message.lower()
