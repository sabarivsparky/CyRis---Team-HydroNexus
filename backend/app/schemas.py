"""
REAL LOGIC — Pydantic v2 models defining the API contract between the
CyRIS backend and the frontend.  These are the typed shapes the UI
consumes.  Every monetary amount is integer INR (field name ends in
``_inr``).  Percentages are floats in [0, 1] named ``*_ratio`` or
``*_prob``.

The frontend is the authority on field names.  Where names differ from
the blueprint, this file uses the frontend's names and the mismatch is
logged in ``docs/DECISIONS.md``.
"""
from __future__ import annotations

import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ═══════════════════════════════════════════════════════════
# 1. CORE DATA MODEL
# ═══════════════════════════════════════════════════════════

class Asset(BaseModel):
    """An enterprise IT asset in the digital twin."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "AST-001",
            "name": "Mobile Banking API Front-End",
            "asset_type": "api_gateway",
            "business_unit": "Digital Channels",
            "criticality": 3,
            "annual_revenue_dependency_inr": 500_000_000,
            "data_sensitivity": 4,
            "internet_facing": True,
            "is_crown_jewel": False,
            "subnet": "Subnet A",
        }]
    })

    id: str = Field(..., description="Unique asset identifier, e.g. 'AST-001'")
    name: str = Field(..., description="Human-readable asset name")
    asset_type: Literal[
        "web_frontend", "api_gateway", "microservice", "database",
        "identity", "application_server", "endpoint_group",
        "network_device", "cloud_workload", "third_party",
    ] = Field(..., description="Asset category")
    business_unit: Literal[
        "Digital Channels", "Core Banking", "Payments",
        "Treasury", "Corporate Banking", "Shared IT",
    ] = Field(..., description="Owning business unit")
    criticality: int = Field(..., ge=1, le=5, description="Criticality 1 (low) – 5 (critical)")
    annual_revenue_dependency_inr: int = Field(..., ge=0, description="Annual revenue dependency in INR")
    data_sensitivity: int = Field(..., ge=1, le=5, description="Data sensitivity 1 (public) – 5 (secret)")
    internet_facing: bool = Field(..., description="True if directly exposed to the internet")
    is_crown_jewel: bool = Field(..., description="True iff criticality == 5")
    subnet: Literal["Subnet A", "Subnet B", "Subnet C"] = Field(
        ..., description="Network zone: Subnet A (DMZ), Subnet B (app tier), Subnet C (core)"
    )


class Vulnerability(BaseModel):
    """A software vulnerability attached to one asset."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "VULN-0001",
            "cve_id": "CVE-2026-1001",
            "asset_id": "AST-001",
            "title": "Remote code execution in API gateway edge",
            "category": "access_control",
            "cvss_score": 8.5,
            "exploitability": 0.72,
            "patch_status": "unpatched",
            "discovered_date": "2026-07-15",
        }]
    })

    id: str = Field(..., description="Unique vulnerability ID, e.g. 'VULN-0001'")
    cve_id: str = Field(..., description="CVE identifier, e.g. 'CVE-2026-1001'")
    asset_id: str = Field(..., description="ID of the asset this vuln belongs to")
    title: str = Field(..., description="Short description of the vulnerability")
    category: Literal[
        "access_control", "patch_management", "network_security",
        "misconfiguration", "data_protection", "logging_monitoring",
    ] = Field(..., description="Vulnerability category")
    cvss_score: float = Field(..., ge=0.0, le=10.0, description="CVSS base score, one decimal")
    exploitability: float = Field(..., ge=0.0, le=1.0, description="Exploitability score 0–1")
    patch_status: Literal["unpatched", "patch_available", "patched"] = Field(
        ..., description="Current patch state"
    )
    discovered_date: datetime.date = Field(..., description="Date the vulnerability was discovered")


class Control(BaseModel):
    """A security control that can be deployed to protect assets."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "CTL-001",
            "name": "Multi-Factor Authentication (privileged + remote)",
            "category": "access_control",
            "cost_inr": 1_800_000,
            "effectiveness": 0.35,
            "impact_reduction": 0.0,
            "dampens_edge_types": {"credential_reuse": 0.6, "token_hijack": 0.4},
            "covered_asset_ids": ["AST-002", "AST-003"],
            "status": "candidate",
            "health": 1.0,
        }]
    })

    id: str = Field(..., description="Unique control ID, e.g. 'CTL-001'")
    name: str = Field(..., description="Human-readable control name")
    category: Literal[
        "access_control", "patch_management", "network_security",
        "misconfiguration", "data_protection", "logging_monitoring",
    ] = Field(..., description="Control category")
    cost_inr: int = Field(..., ge=0, description="First-year total cost in INR")
    effectiveness: float = Field(..., ge=0.0, le=1.0,
                                 description="Reduction in compromise probability (0–1)")
    impact_reduction: float = Field(0.0, ge=0.0, le=1.0,
                                    description="Reduction in loss magnitude per incident (0–1)")
    dampens_edge_types: dict[str, float] = Field(
        default_factory=dict,
        description="Edge relationship types dampened and by how much, "
                    "e.g. {'credential_reuse': 0.6}",
    )
    covered_asset_ids: list[str] = Field(
        default_factory=list,
        description="Asset IDs this control protects",
    )
    status: Literal["deployed", "candidate"] = Field(
        ..., description="Current deployment status"
    )
    health: float = Field(1.0, ge=0.0, le=1.0,
                          description="Control health 0–1; <1 = degraded")


class ExploitEdge(BaseModel):
    """A directed edge in the attack-path graph."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "source": "INTERNET",
            "target": "AST-001",
            "relationship_type": "network_access",
            "exploit_probability": 0.90,
            "description": "Public ingress to API gateway",
        }]
    })

    source: str = Field(..., description="Source asset ID or 'INTERNET'")
    target: str = Field(..., description="Target asset ID")
    relationship_type: Literal[
        "network_access", "service_call", "credential_reuse",
        "token_hijack", "trust_relationship", "data_flow",
    ] = Field(..., description="Type of lateral-movement technique")
    exploit_probability: float = Field(..., gt=0.0, le=1.0,
                                       description="Probability of successful exploit (0, 1]")
    description: str = Field(..., description="Human-readable description of the pivot")


class Dataset(BaseModel):
    """Complete synthetic dataset for the digital twin."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "assets": [],
            "vulnerabilities": [],
            "controls": [],
            "edges": [],
            "as_of": "2026-09-28",
        }]
    })

    assets: list[Asset]
    vulnerabilities: list[Vulnerability]
    controls: list[Control]
    edges: list[ExploitEdge]
    as_of: datetime.date


# ═══════════════════════════════════════════════════════════
# 2. TWIN GRAPH VIEW (for the Digital Twin panel)
# ═══════════════════════════════════════════════════════════

class TwinGraphNode(BaseModel):
    """A node in the twin graph view, shaped for the UI graph panel."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "n-jewel", "name": "Core transaction vault",
            "type": "crown-jewel", "criticality": "critical",
            "ealContribution": 42_000_000, "status": "exposed",
            "x": 900, "y": 180, "dependencies": ["n-identity"],
            "is_crown_jewel": True, "on_active_path": True,
            "eal_inr": 42_000_000,
        }]
    })

    id: str = Field(..., description="Node identifier")
    name: str = Field(..., description="Display name")
    type: Literal[
        "asset", "identity", "control", "vulnerability",
        "crown-jewel", "external",
    ] = Field(..., description="Visual node type for the UI")
    criticality: Literal["critical", "high", "medium", "low", "nominal"] = Field(
        ..., description="Severity level"
    )
    ealContribution: int = Field(0, ge=0, description="EAL contribution in INR")
    status: Literal[
        "exposed", "monitored", "hardened", "absent", "degraded", "active", "proposed",
    ] = Field(..., description="Node status for styling")
    x: float = Field(0, description="X position for layout")
    y: float = Field(0, description="Y position for layout")
    dependencies: list[str] = Field(default_factory=list, description="IDs of predecessor nodes")
    is_crown_jewel: bool = Field(False, description="True if this is a crown-jewel asset")
    on_active_path: bool = Field(False, description="True if on an active path")
    eal_inr: int = Field(0, ge=0, description="EAL for this asset in INR")


class TwinGraphEdge(BaseModel):
    """An edge in the twin graph view."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "e1", "source": "n-internet", "target": "n-api",
            "kind": "attack", "label": "Public ingress",
        }]
    })

    id: str = Field(..., description="Edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    kind: Literal["attack", "control", "identity"] = Field(
        ..., description="Visual edge type"
    )
    label: str = Field(..., description="Edge label for tooltip")


class TwinGraphView(BaseModel):
    """Complete graph data for the Digital Twin panel."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"nodes": [], "edges": []}]
    })

    nodes: list[TwinGraphNode]
    edges: list[TwinGraphEdge]


# ═══════════════════════════════════════════════════════════
# 3. RISK SUMMARY
# ═══════════════════════════════════════════════════════════

class HistogramBin(BaseModel):
    """One bin in the loss distribution histogram."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"lower_inr": 0, "upper_inr": 100_000, "probability": 0.05}]
    })
    lower_inr: int = Field(..., description="Lower bound of the bin in INR")
    upper_inr: int = Field(..., description="Upper bound of the bin in INR")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability mass in this bin")


class ExceedancePoint(BaseModel):
    """One point on the loss exceedance curve."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"loss_inr": 500_000, "prob_exceed": 0.30}]
    })
    loss_inr: int = Field(..., description="Loss threshold in INR")
    prob_exceed: float = Field(..., ge=0.0, le=1.0, description="P(annual_loss > loss_inr)")


class RiskSummary(BaseModel):
    """Organization-level risk summary for the dashboard."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "eal_inr": 4_200_000, "var95_inr": 12_000_000,
            "var99_inr": 24_000_000, "cvar95_inr": 18_000_000,
            "as_of": "2026-09-28", "histogram": [], "exceedance_curve": [],
        }]
    })

    eal_inr: int = Field(..., ge=0, description="Expected Annual Loss in INR")
    var95_inr: int = Field(..., ge=0, description="95th-percentile Value at Risk in INR")
    var99_inr: int = Field(..., ge=0, description="99th-percentile Value at Risk in INR")
    cvar95_inr: int = Field(0, ge=0, description="Conditional VaR at 95th percentile in INR")
    as_of: datetime.date = Field(..., description="Date of the simulation snapshot")
    histogram: list[HistogramBin] = Field(default_factory=list, description="Loss distribution histogram")
    exceedance_curve: list[ExceedancePoint] = Field(default_factory=list, description="Exceedance curve")


# ═══════════════════════════════════════════════════════════
# 4. RISK CONTRIBUTORS
# ═══════════════════════════════════════════════════════════

class RiskContributor(BaseModel):
    """A top risk contributor for the dashboard panel.

    Note: the frontend uses ``eal`` (not ``eal_inr``) and ``share`` (not
    ``share_ratio``).  We keep the frontend names here and document the
    mismatch in DECISIONS.md.
    """
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "c1", "name": "Privileged identity hop to vault",
            "level": "asset", "eal_inr": 27_000_000, "share_ratio": 0.64,
            "pathId": "path-7", "eal": 27_000_000, "share": 0.64,
            "severity": "critical",
        }]
    })

    id: str = Field(..., description="Contributor identifier")
    name: str = Field(..., description="Human-readable contributor name")
    level: Literal["asset", "vulnerability", "business_unit"] = Field(
        "asset", description="Granularity level"
    )
    eal_inr: int = Field(..., ge=0, description="EAL contribution in INR")
    share_ratio: float = Field(..., ge=0.0, le=1.0, description="Share of total EAL")

    # Frontend also uses pathId and severity; we include them for
    # compatibility but they are optional from the backend.
    pathId: str = Field("", description="Related attack path ID (frontend compat)")
    eal: int = Field(0, ge=0, description="Frontend-compat alias for eal_inr")
    share: float = Field(0.0, ge=0.0, le=1.0, description="Frontend-compat alias for share_ratio")
    severity: Literal["critical", "high", "medium", "low", "nominal"] = Field(
        "medium", description="Severity level for display"
    )


# ═══════════════════════════════════════════════════════════
# 5. TREND
# ═══════════════════════════════════════════════════════════

class TrendPoint(BaseModel):
    """One point in the EAL trend chart.

    Frontend uses ``label`` (month name) and ``eal`` (integer INR).
    """
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"label": "Sep", "eal": 4_200_000, "timestamp": "2026-09-28T00:00:00Z", "eal_inr": 4_200_000}]
    })

    label: str = Field(..., description="Time label, e.g. 'Sep'")
    eal: int = Field(..., ge=0, description="EAL in INR at this point")
    timestamp: str = Field("", description="ISO timestamp (optional)")
    eal_inr: int = Field(0, ge=0, description="Backend-canonical alias")


# ═══════════════════════════════════════════════════════════
# 6. ATTACK PATHS
# ═══════════════════════════════════════════════════════════

class AttackPathStep(BaseModel):
    """One step in an attack path."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"source": "AST-001", "target": "AST-002", "technique": "credential_reuse", "probability": 0.55}]
    })
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    technique: str = Field(..., description="Technique / relationship type used")
    probability: float = Field(..., ge=0.0, le=1.0, description="Step probability")


class AttackPath(BaseModel):
    """A ranked attack path from INTERNET to a crown jewel.

    Frontend uses ``nodeIds``, ``edgeIds``, ``ealContribution``,
    ``hopsToCrownJewel``.  We support both frontend and backend names.
    """
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "path-7",
            "name": "Attack Path #7 — VPN/API to vault",
            "nodes": ["INTERNET", "AST-001", "AST-002", "AST-003", "AST-004"],
            "steps": [],
            "path_probability": 0.089,
            "blast_radius_eal_inr": 27_000_000,
            "nodeIds": ["n-internet", "n-api", "n-auth", "n-identity", "n-jewel"],
            "edgeIds": ["e1", "e3", "e4", "e5"],
            "ealContribution": 27_000_000,
            "hopsToCrownJewel": 4,
        }]
    })

    id: str = Field(..., description="Path identifier")
    name: str = Field(..., description="Human-readable path name")
    nodes: list[str] = Field(default_factory=list, description="Ordered node IDs (backend)")
    steps: list[AttackPathStep] = Field(default_factory=list, description="Step-by-step breakdown")
    path_probability: float = Field(0.0, ge=0.0, le=1.0, description="End-to-end probability")
    blast_radius_eal_inr: int = Field(0, ge=0, description="Blast radius EAL in INR")

    # Frontend-compat fields
    nodeIds: list[str] = Field(default_factory=list, description="Frontend: ordered node IDs")
    edgeIds: list[str] = Field(default_factory=list, description="Frontend: ordered edge IDs")
    ealContribution: int = Field(0, ge=0, description="Frontend: EAL contribution in INR")
    hopsToCrownJewel: int = Field(0, ge=0, description="Frontend: hops to crown jewel")


# ═══════════════════════════════════════════════════════════
# 7. WHAT-IF
# ═══════════════════════════════════════════════════════════

class WhatIfRequest(BaseModel):
    """Request to simulate a what-if scenario."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "mutations": [{"type": "deploy_control", "control_id": "CTL-001"}],
            "n_iterations": 10_000,
            "seed": 42,
        }]
    })

    mutations: list[dict[str, Any]] = Field(
        ..., description="List of mutation dicts to apply"
    )
    n_iterations: int = Field(10_000, ge=1_000, description="Monte Carlo iterations")
    seed: int = Field(42, description="RNG seed")


class WhatIfResult(BaseModel):
    """Result of a what-if simulation."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "before_eal_inr": 4_200_000, "after_eal_inr": 3_350_000,
            "delta_inr": -850_000, "delta_ratio": -0.2024,
            "cost_inr": 1_800_000, "rosi": 0.47,
        }]
    })

    before_eal_inr: int = Field(..., ge=0)
    after_eal_inr: int = Field(..., ge=0)
    delta_inr: int = Field(...)
    delta_ratio: float = Field(...)
    cost_inr: int = Field(0, ge=0)
    rosi: float = Field(0.0, description="Return on Security Investment ratio")


# ═══════════════════════════════════════════════════════════
# 8. COUNTERFACTUAL CARDS
# ═══════════════════════════════════════════════════════════

class CounterfactualCard(BaseModel):
    """A pre-computed what-if card for a candidate control.

    Frontend ``CounterfactualScenario`` uses: id, controlId, title,
    proposedAction.  We include both sets of fields.
    """
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "cf-mfa", "controlId": "ctrl-mfa",
            "title": "Break the identity hop",
            "action": "Enable MFA for privileged accounts",
            "proposedAction": "Enable MFA for privileged accounts",
            "eal_before_inr": 4_200_000, "eal_after_inr": 3_350_000,
            "cost_inr": 1_800_000, "rosi": 0.47,
        }]
    })

    id: str = Field(...)
    controlId: str = Field(..., description="Related control ID (frontend key)")
    title: str = Field(...)
    action: str = Field("", description="Backend: action description")
    proposedAction: str = Field("", description="Frontend: proposed action text")
    eal_before_inr: int = Field(0, ge=0)
    eal_after_inr: int = Field(0, ge=0)
    cost_inr: int = Field(0, ge=0)
    rosi: float = Field(0.0)


# ═══════════════════════════════════════════════════════════
# 9. OPTIMIZER
# ═══════════════════════════════════════════════════════════

class OptimizerCurvePoint(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"budget_inr": 1_000_000, "eal_reduction_inr": 500_000}]
    })
    budget_inr: int = Field(..., ge=0)
    eal_reduction_inr: int = Field(..., ge=0)


class OptimizerRequest(BaseModel):
    """Budget optimization request."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"budget_inr": 5_000_000}]
    })
    budget_inr: int = Field(..., ge=0, description="Total budget in INR")


class OptimizerResult(BaseModel):
    """Result of the budget optimizer."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "selected_control_ids": ["CTL-001"],
            "total_cost_inr": 1_800_000,
            "eal_reduction_inr": 850_000,
            "curve": [],
            "selectedIds": ["CTL-001"],
            "estimatedCost": 1_800_000,
            "riskReduction": 850_000,
            "resultingEal": 3_350_000,
            "rosi": 0.47,
            "remainingBudget": 3_200_000,
        }]
    })

    selected_control_ids: list[str] = Field(default_factory=list)
    total_cost_inr: int = Field(0, ge=0)
    eal_reduction_inr: int = Field(0, ge=0)
    curve: list[OptimizerCurvePoint] = Field(default_factory=list)

    # Frontend-compat fields (OptimizationResult interface)
    selectedIds: list[str] = Field(default_factory=list)
    estimatedCost: int = Field(0, ge=0)
    riskReduction: int = Field(0, ge=0)
    resultingEal: int = Field(0, ge=0)
    rosi: float = Field(0.0)
    remainingBudget: int = Field(0, ge=0)


# ═══════════════════════════════════════════════════════════
# 10. AGENT DEBATE
# ═══════════════════════════════════════════════════════════

class AgentEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "ev-r1", "label": "Qualys finding",
            "source": "Qualys VMDR",
            "detail": "CVE-2026-3827 CVSS 9.8 on mobile-banking-api-prod, unauthenticated RCE.",
        }]
    })
    id: str = Field(...)
    label: str = Field(...)
    source: str = Field(...)
    detail: str = Field(...)


class RedFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "finding": "CVE-2026-3827 establishes an open exploit path.",
            "attackVector": "Public API RCE → env-var pivot → K8s SA token hijack → AD principal → vault",
            "affectedAsset": "Core transaction vault (crown jewel)",
            "estimatedImpact": 27_000_000,
            "evidence": [],
        }]
    })
    finding: str = Field(...)
    attackVector: str = Field(...)
    affectedAsset: str = Field(...)
    estimatedImpact: int = Field(..., ge=0)
    evidence: list[AgentEvidence] = Field(default_factory=list)


class BlueResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "existingControl": "CrowdStrike Falcon behavioral isolation.",
            "mitigation": "Host isolation can interrupt post-exploit tooling.",
            "residualRisk": "Privileged non-human identity still authenticates with a static secret.",
            "counterargument": "The identity hop is not covered.",
            "evidence": [],
        }]
    })
    existingControl: str = Field(...)
    mitigation: str = Field(...)
    residualRisk: str = Field(...)
    counterargument: str = Field(...)
    evidence: list[AgentEvidence] = Field(default_factory=list)


class JudgeDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "synthesizedFinding": "The exploit is real and the twin confirms a live lateral path.",
            "financialImpact": 27_000_000,
            "confidence": 0.86,
            "evidenceState": "grounded",
            "recommendedAction": "Enable phishing-resistant MFA for privileged accounts.",
            "recommendedControlId": "ctrl-mfa",
        }]
    })
    synthesizedFinding: str = Field(...)
    financialImpact: int = Field(..., ge=0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidenceState: Literal["partial", "grounded", "contested"] = Field(...)
    recommendedAction: str = Field(...)
    recommendedControlId: str = Field(...)


class AgentDebateResult(BaseModel):
    """Full agent debate record.  Frontend type: ``AgentRecord``."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "debate-mfa",
            "title": "Privileged path to transaction vault",
            "relatedControlId": "ctrl-mfa",
            "red": {
                "finding": "CVE-2026-3827 establishes an open exploit path.",
                "attackVector": "Public API RCE → env-var pivot",
                "affectedAsset": "Core transaction vault",
                "estimatedImpact": 27_000_000,
                "evidence": [],
            },
            "blue": {
                "existingControl": "CrowdStrike Falcon",
                "mitigation": "Host isolation",
                "residualRisk": "Privileged non-human identity",
                "counterargument": "Identity hop not covered",
                "evidence": [],
            },
            "judge": {
                "synthesizedFinding": "The exploit is real.",
                "financialImpact": 27_000_000,
                "confidence": 0.86,
                "evidenceState": "grounded",
                "recommendedAction": "Enable MFA",
                "recommendedControlId": "ctrl-mfa",
            },
        }]
    })

    id: str = Field(...)
    title: str = Field(...)
    relatedControlId: str = Field(...)
    red: RedFinding = Field(...)
    blue: BlueResponse = Field(...)
    judge: JudgeDecision = Field(...)


# ═══════════════════════════════════════════════════════════
# 11. NATURAL LANGUAGE QUERY
# ═══════════════════════════════════════════════════════════

class NLQueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"query": "What is our current EAL?"}]
    })
    query: str = Field(..., description="Natural-language question")


class NLQueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "answer": "Your current Expected Annual Loss is ₹42 Lakh.",
            "data": {"eal_inr": 4_200_000},
        }]
    })
    answer: str = Field(..., description="Natural-language answer")
    data: dict[str, Any] | None = Field(None, description="Optional structured data payload")


# ═══════════════════════════════════════════════════════════
# 12. COMPLIANCE MAPPING
# ═══════════════════════════════════════════════════════════

class ComplianceMapping(BaseModel):
    """Maps a finding to regulatory framework clauses.

    Frontend type: ``ComplianceRow``.
    """
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "cmp-1", "finding": "Unpatched gateway CVE-2026-3827",
            "control": "Access control / subnet isolation",
            "framework": "SEBI CSCRF",
            "clause": "Section 4.2 (Access Management & Network Controls)",
            "status": "gap",
            "evidence": "Twin path #7 still open; MFA control node ABSENT",
            "proof": "unverified",
            "proofRef": "PROOF-PENDING-CSCRF-4.2",
        }]
    })

    id: str = Field(...)
    finding: str = Field(...)
    control: str = Field(...)
    framework: Literal["ISO 27001", "NIST CSF", "RBI CSF", "SEBI CSCRF"] = Field(...)
    clause: str = Field(...)
    status: Literal["mapped", "gap", "in-progress"] = Field(...)
    evidence: str = Field(...)
    proof: Literal["verified", "unverified", "pending"] = Field(...)
    proofRef: str = Field(...)


# ═══════════════════════════════════════════════════════════
# 13. AUDIT RECORD
# ═══════════════════════════════════════════════════════════

class AuditRecord(BaseModel):
    """Immutable audit record for every twin state change."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "audit-001",
            "timestamp": "2026-09-28T08:00:00Z",
            "action": "deploy_control",
            "actor": "system",
            "twin_version": 1,
            "twin_fingerprint": "abc123",
            "details": {"control_id": "CTL-001"},
        }]
    })

    id: str = Field(...)
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    action: str = Field(..., description="What was done")
    actor: str = Field("system", description="Who/what performed the action")
    twin_version: int = Field(..., ge=0)
    twin_fingerprint: str = Field(...)
    details: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# 14. TELEMETRY EVENT
# ═══════════════════════════════════════════════════════════

class TelemetryEvent(BaseModel):
    """Real-time telemetry event.  Frontend type with same name."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "id": "tel-001",
            "timestamp": "2026-09-24T04:31:00.000Z",
            "event": "Baseline platform EAL established from live twin",
            "source": "Digital Twin",
            "severity": "nominal",
            "ealImpact": 0,
            "status": "nominal",
            "eal_after_inr": 4_200_000,
            "event_type": "baseline_established",
            "message": "Baseline EAL computed.",
        }]
    })

    id: str = Field(...)
    timestamp: str = Field(..., description="ISO-8601 timestamp")
    event: str = Field(..., description="Event description")
    source: Literal[
        "Control Change", "Scanner", "SIEM", "Digital Twin",
        "Budget Optimizer", "Agent Judge", "Ingestion",
    ] = Field(...)
    severity: Literal["critical", "high", "medium", "low", "nominal"] = Field(...)
    ealImpact: int = Field(0, description="EAL impact in INR (frontend name)")
    status: Literal["open", "absorbed", "approved", "nominal"] = Field(...)
    eal_after_inr: int = Field(0, ge=0, description="EAL after this event (backend)")
    event_type: str = Field("", description="Machine-readable event type")
    message: str = Field("", description="Detailed message")


# ═══════════════════════════════════════════════════════════
# 15. REMEDIATION APPROVAL
# ═══════════════════════════════════════════════════════════

class RemediationApprovalRequest(BaseModel):
    """Approve a remediation action."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"control_id": "CTL-001", "approved_by": "CISO"}]
    })
    control_id: str = Field(...)
    approved_by: str = Field("board", description="Who approved")


class RemediationApprovalResponse(BaseModel):
    """Response after approving a remediation."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"control_id": "CTL-001", "status": "approved", "message": "Control deployed."}]
    })
    control_id: str = Field(...)
    status: str = Field(...)
    message: str = Field("")


# ═══════════════════════════════════════════════════════════
# 16. HEALTH CHECK
# ═══════════════════════════════════════════════════════════

class HealthResponse(BaseModel):
    """Health check response."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"status": "ok", "version": "0.1.0", "twin_loaded": True}]
    })
    status: Literal["ok"] = "ok"
    version: str = "0.1.0"
    twin_loaded: bool = False


# ═══════════════════════════════════════════════════════════
# 17. SIMULATION RESULT (Phase 2 — risk engine output)
# ═══════════════════════════════════════════════════════════

class SLEComponents(BaseModel):
    """Six-component SLE breakdown for an asset."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "downtime_inr": 100_000, "breach_inr": 200_000,
            "recovery_inr": 50_000, "regulatory_inr": 0,
            "operational_inr": 0, "reputation_inr": 0,
        }]
    })
    downtime_inr: int = Field(0, ge=0)
    breach_inr: int = Field(0, ge=0)
    recovery_inr: int = Field(0, ge=0)
    regulatory_inr: int = Field(0, ge=0)
    operational_inr: int = Field(0, ge=0)
    reputation_inr: int = Field(0, ge=0)


class VulnContribution(BaseModel):
    """Attribution of risk to a specific vulnerability."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"vuln_id": "VULN-0001", "cve_id": "CVE-2026-1001", "contribution_inr": 100_000}]
    })
    vuln_id: str
    cve_id: str
    contribution_inr: int = Field(0, ge=0)


class AssetRisk(BaseModel):
    """Per-asset risk output from the simulation."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "asset_id": "AST-004", "name": "Core Transaction Database Vault",
            "business_unit": "Core Banking",
            "lambda_": 0.05, "sle_inr": 18_000_000,
            "sle_components": {
                "downtime_inr": 2_000_000, "breach_inr": 6_000_000,
                "recovery_inr": 4_500_000, "regulatory_inr": 5_000_000,
                "operational_inr": 3_500_000, "reputation_inr": 2_000_000,
            },
            "p_raw": 0.6, "freq_mult": 0.85, "mag_mult": 0.65,
            "p_comp": 0.51, "reach": 0.10,
            "eal_inr": 900_000, "var95_inr": 4_000_000, "var99_inr": 8_000_000,
            "top_vulnerabilities": [], "best_path": ["INTERNET", "AST-001", "AST-002", "AST-003", "AST-004"],
        }]
    })

    asset_id: str
    name: str
    business_unit: str
    lambda_: float = Field(..., ge=0.0, description="Annual loss event rate")
    sle_inr: int = Field(..., ge=0)
    sle_components: SLEComponents
    p_raw: float = Field(..., ge=0.0, le=1.0)
    freq_mult: float = Field(..., ge=0.0, le=1.0)
    mag_mult: float = Field(..., ge=0.0, le=1.0)
    p_comp: float = Field(..., ge=0.0, le=1.0)
    reach: float = Field(..., ge=0.0, le=1.0)
    eal_inr: int = Field(..., ge=0)
    var95_inr: int = Field(..., ge=0)
    var99_inr: int = Field(..., ge=0)
    top_vulnerabilities: list[VulnContribution] = Field(default_factory=list)
    best_path: list[str] = Field(default_factory=list, description="Best path from INTERNET")


class BusinessUnitRisk(BaseModel):
    """Per-BU risk output."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"business_unit": "Payments", "eal_inr": 100_000, "var95_inr": 300_000, "var99_inr": 500_000}]
    })
    business_unit: str
    eal_inr: int = Field(..., ge=0)
    var95_inr: int = Field(..., ge=0)
    var99_inr: int = Field(..., ge=0)


class OrgRisk(BaseModel):
    """Organization-level risk output."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"eal_inr": 1_000_000, "var95_inr": 3_000_000, "var99_inr": 5_000_000}]
    })
    eal_inr: int = Field(..., ge=0)
    var95_inr: int = Field(..., ge=0)
    var99_inr: int = Field(..., ge=0)
    cvar95_inr: int = Field(0, ge=0)
    histogram: list[HistogramBin] = Field(default_factory=list)
    exceedance_curve: list[ExceedancePoint] = Field(default_factory=list)


class SimulationMeta(BaseModel):
    """Metadata about a simulation run."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "n_iterations": 10_000, "seed": 42,
            "twin_version": 0, "twin_fingerprint": "abc123",
            "runtime_ms": 1500.0, "as_of": "2026-09-28",
        }]
    })
    n_iterations: int
    seed: int
    twin_version: int
    twin_fingerprint: str
    runtime_ms: float
    as_of: datetime.date


class SimulationResult(BaseModel):
    """Complete output of run_simulation()."""
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{
            "org": {"eal_inr": 1_000_000, "var95_inr": 3_000_000, "var99_inr": 5_000_000},
            "business_units": [],
            "assets": [],
            "meta": {
                "n_iterations": 10_000, "seed": 42,
                "twin_version": 0, "twin_fingerprint": "abc123",
                "runtime_ms": 1500.0, "as_of": "2026-09-28",
            },
        }]
    })

    org: OrgRisk
    business_units: list[BusinessUnitRisk]
    assets: list[AssetRisk] = Field(..., description="Assets sorted by eal_inr descending")
    meta: SimulationMeta

    # Non-serialized field for tests/internal: raw numpy arrays
    # This is excluded from JSON serialization by default.
    _raw_arrays: Any = None


# ═══════════════════════════════════════════════════════════
# 18. AUDIT VERIFY
# ═══════════════════════════════════════════════════════════

class AuditVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"record_id": "audit-001"}]
    })
    record_id: str = Field(...)


class AuditVerifyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "examples": [{"record_id": "audit-001", "verified": True, "message": "Signature valid."}]
    })
    record_id: str
    verified: bool
    message: str = ""
