"""
REAL LOGIC — Tests for Pydantic v2 schema models.

Every model:
  1. Instantiates from its own json_schema_extra example.
  2. Round-trips through .model_dump_json() → .model_validate_json().
  3. Rejects an unknown extra field (extra="forbid").
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import (
    Asset,
    Vulnerability,
    Control,
    ExploitEdge,
    Dataset,
    TwinGraphNode,
    TwinGraphEdge,
    TwinGraphView,
    HistogramBin,
    ExceedancePoint,
    RiskSummary,
    RiskContributor,
    TrendPoint,
    AttackPathStep,
    AttackPath,
    WhatIfRequest,
    WhatIfResult,
    CounterfactualCard,
    OptimizerCurvePoint,
    OptimizerRequest,
    OptimizerResult,
    AgentEvidence,
    RedFinding,
    BlueResponse,
    JudgeDecision,
    AgentDebateResult,
    NLQueryRequest,
    NLQueryResponse,
    ComplianceMapping,
    AuditRecord,
    TelemetryEvent,
    RemediationApprovalRequest,
    RemediationApprovalResponse,
    HealthResponse,
    SLEComponents,
    VulnContribution,
    AssetRisk,
    BusinessUnitRisk,
    OrgRisk,
    SimulationMeta,
    SimulationResult,
    AuditVerifyRequest,
    AuditVerifyResponse,
)


# ── Helpers ───────────────────────────────────────────────

def _get_example(model_cls: type) -> dict:
    """Extract the first example from json_schema_extra."""
    config = getattr(model_cls, "model_config", {})
    if isinstance(config, dict):
        schema_extra = config.get("json_schema_extra")
    else:
        schema_extra = getattr(config, "json_schema_extra", None)

    if schema_extra and isinstance(schema_extra, dict) and "examples" in schema_extra:
        return schema_extra["examples"][0]
    raise ValueError(f"No json_schema_extra for {model_cls.__name__}")


def _roundtrip_test(model_cls: type, data: dict) -> None:
    """Instantiate, dump to JSON, parse back, and compare."""
    obj = model_cls.model_validate(data)
    json_str = obj.model_dump_json()
    obj2 = model_cls.model_validate_json(json_str)
    assert obj.model_dump() == obj2.model_dump()


def _extra_field_test(model_cls: type, data: dict) -> None:
    """Ensure an unknown field raises ValidationError."""
    bad = {**data, "totally_unknown_field_xyz": 42}
    with pytest.raises(ValidationError):
        model_cls.model_validate(bad)


# ── Models with json_schema_extra ─────────────────────────

MODELS_WITH_EXAMPLES = [
    Asset,
    Vulnerability,
    Control,
    ExploitEdge,
    Dataset,
    TwinGraphNode,
    TwinGraphEdge,
    RiskSummary,
    RiskContributor,
    TrendPoint,
    AttackPath,
    WhatIfRequest,
    WhatIfResult,
    CounterfactualCard,
    OptimizerRequest,
    OptimizerResult,
    AgentEvidence,
    RedFinding,
    BlueResponse,
    JudgeDecision,
    AgentDebateResult,
    NLQueryRequest,
    NLQueryResponse,
    ComplianceMapping,
    AuditRecord,
    TelemetryEvent,
    RemediationApprovalRequest,
    RemediationApprovalResponse,
    HealthResponse,
    AuditVerifyRequest,
    AuditVerifyResponse,
    SLEComponents,
    VulnContribution,
    AssetRisk,
    BusinessUnitRisk,
    OrgRisk,
    SimulationMeta,
    SimulationResult,
    HistogramBin,
    ExceedancePoint,
    AttackPathStep,
    OptimizerCurvePoint,
]


@pytest.mark.parametrize("model_cls", MODELS_WITH_EXAMPLES, ids=lambda m: m.__name__)
def test_instantiate_from_example(model_cls: type) -> None:
    """Each model instantiates cleanly from its own example."""
    data = _get_example(model_cls)
    obj = model_cls.model_validate(data)
    assert obj is not None


@pytest.mark.parametrize("model_cls", MODELS_WITH_EXAMPLES, ids=lambda m: m.__name__)
def test_roundtrip_json(model_cls: type) -> None:
    """Round-trip: model_dump_json → model_validate_json."""
    data = _get_example(model_cls)
    _roundtrip_test(model_cls, data)


@pytest.mark.parametrize("model_cls", MODELS_WITH_EXAMPLES, ids=lambda m: m.__name__)
def test_rejects_extra_field(model_cls: type) -> None:
    """extra='forbid' rejects unknown fields."""
    data = _get_example(model_cls)
    _extra_field_test(model_cls, data)


# ── Models without json_schema_extra (build manually) ─────

def test_histogram_bin() -> None:
    data = {"lower_inr": 0, "upper_inr": 100_000, "probability": 0.05}
    _roundtrip_test(HistogramBin, data)
    _extra_field_test(HistogramBin, data)


def test_exceedance_point() -> None:
    data = {"loss_inr": 500_000, "prob_exceed": 0.30}
    _roundtrip_test(ExceedancePoint, data)
    _extra_field_test(ExceedancePoint, data)


def test_attack_path_step() -> None:
    data = {"source": "AST-001", "target": "AST-002", "technique": "credential_reuse", "probability": 0.55}
    _roundtrip_test(AttackPathStep, data)
    _extra_field_test(AttackPathStep, data)


def test_optimizer_curve_point() -> None:
    data = {"budget_inr": 1_000_000, "eal_reduction_inr": 500_000}
    _roundtrip_test(OptimizerCurvePoint, data)
    _extra_field_test(OptimizerCurvePoint, data)


def test_sle_components() -> None:
    data = {
        "downtime_inr": 100_000, "breach_inr": 200_000,
        "recovery_inr": 50_000, "regulatory_inr": 0,
        "operational_inr": 0, "reputation_inr": 0,
    }
    _roundtrip_test(SLEComponents, data)
    _extra_field_test(SLEComponents, data)


def test_vuln_contribution() -> None:
    data = {"vuln_id": "VULN-0001", "cve_id": "CVE-2026-1001", "contribution_inr": 100_000}
    _roundtrip_test(VulnContribution, data)
    _extra_field_test(VulnContribution, data)


def test_asset_risk() -> None:
    data = {
        "asset_id": "AST-001", "name": "Test", "business_unit": "Payments",
        "lambda_": 0.1, "sle_inr": 500_000,
        "sle_components": {
            "downtime_inr": 100_000, "breach_inr": 200_000,
            "recovery_inr": 50_000, "regulatory_inr": 0,
            "operational_inr": 100_000, "reputation_inr": 50_000,
        },
        "p_raw": 0.5, "freq_mult": 0.8, "mag_mult": 0.9,
        "p_comp": 0.4, "reach": 0.3, "eal_inr": 50_000,
        "var95_inr": 150_000, "var99_inr": 250_000,
        "top_vulnerabilities": [], "best_path": [],
    }
    _roundtrip_test(AssetRisk, data)
    _extra_field_test(AssetRisk, data)


def test_business_unit_risk() -> None:
    data = {"business_unit": "Payments", "eal_inr": 100_000, "var95_inr": 300_000, "var99_inr": 500_000}
    _roundtrip_test(BusinessUnitRisk, data)
    _extra_field_test(BusinessUnitRisk, data)


def test_org_risk() -> None:
    data = {"eal_inr": 1_000_000, "var95_inr": 3_000_000, "var99_inr": 5_000_000}
    _roundtrip_test(OrgRisk, data)
    _extra_field_test(OrgRisk, data)


def test_simulation_meta() -> None:
    data = {
        "n_iterations": 10_000, "seed": 42,
        "twin_version": 0, "twin_fingerprint": "abc123",
        "runtime_ms": 1500.0, "as_of": "2026-09-28",
    }
    _roundtrip_test(SimulationMeta, data)
    _extra_field_test(SimulationMeta, data)


def test_simulation_result() -> None:
    data = {
        "org": {"eal_inr": 1_000_000, "var95_inr": 3_000_000, "var99_inr": 5_000_000},
        "business_units": [],
        "assets": [],
        "meta": {
            "n_iterations": 10_000, "seed": 42,
            "twin_version": 0, "twin_fingerprint": "abc123",
            "runtime_ms": 1500.0, "as_of": "2026-09-28",
        },
    }
    _roundtrip_test(SimulationResult, data)
    _extra_field_test(SimulationResult, data)


def test_twin_graph_view() -> None:
    data = {"nodes": [], "edges": []}
    _roundtrip_test(TwinGraphView, data)
    _extra_field_test(TwinGraphView, data)
