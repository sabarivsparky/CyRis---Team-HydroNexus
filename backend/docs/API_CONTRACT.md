# CyRIS API Contract

> **Version:** 0.1.0 | **Date:** 2026-09-28
>
> This document specifies every endpoint the CyRIS backend exposes across phases.

---

## Endpoint Table

| Method | Path | Request Model | Response Model | UI Panel | Phase |
|--------|------|---------------|----------------|----------|-------|
| GET | `/api/v1/health` | — | `HealthResponse` | Header / status bar | 3 |
| GET | `/api/v1/risk/summary` | — | `RiskSummary` | Dashboard (EALHero, VaR cards, histogram) | 3 |
| GET | `/api/v1/risk/contributors?level=asset\|vulnerability\|business_unit` | query param `level` | `list[RiskContributor]` | Dashboard (RiskContributors) | 3 |
| GET | `/api/v1/risk/trend` | — | `list[TrendPoint]` | Dashboard (RiskTrendChart) | 3 |
| GET | `/api/v1/twin/graph` | — | `TwinGraphView` | Digital Twin (RiskGraph) | 4 |
| GET | `/api/v1/attack-paths` | — | `list[AttackPath]` | Digital Twin (AttackPathPanel) | 4 |
| GET | `/api/v1/attack-paths/chokepoints` | query param `limit` | `list[Chokepoint]` | Attack Path Panel | 4 |
| GET | `/api/v1/assets/{asset_id}` | path param `asset_id` | `AssetDetail` | Node Inspector | 4 |
| POST | `/api/v1/whatif` | `WhatIfRequest` | `WhatIfResult` | What-If Sandbox | 5 |
| GET | `/api/v1/whatif/presets` | — | `list[WhatIfPreset]` | What-If Sandbox | 5 |
| GET | `/api/v1/counterfactuals` | query param `limit` | `list[CounterfactualCard]` | Counterfactuals page | 5 |
| POST | `/api/v1/optimizer/run` | `OptimizerRequest` | `OptimizerResult` | Budget Optimizer | 6 |
| POST | `/api/v1/agents/debate` | — (trigger) | `AgentDebateResult` | Red/Blue/Judge Agents page | 7 |
| POST | `/api/v1/query` | `NLQueryRequest` | `NLQueryResponse` | Natural Language Query bar | 7 |
| GET | `/api/v1/compliance/mappings` | — | `list[ComplianceMapping]` | Compliance Mapping table | 8 |
| GET | `/api/v1/audit/records` | — | `list[AuditRecord]` | Audit Trail page | 8 |
| POST | `/api/v1/audit/verify` | `AuditVerifyRequest` | `AuditVerifyResponse` | Audit Trail (verify button) | 8 |
| GET | `/api/v1/telemetry/events` | — | `list[TelemetryEvent]` | Telemetry Timeline | 9 |
| SSE/WS | `/api/v1/stream/telemetry` | — | `TelemetryEvent` (stream) | Live Telemetry feed | 9 |
| POST | `/api/v1/remediations/approve` | `RemediationApprovalRequest` | `RemediationApprovalResponse` | Counterfactuals (approve button) | 10 |

---

## Notes

1. **Money convention:** Every monetary field is integer INR and ends in `_inr`. The frontend formats for display.
2. **Percentage convention:** Floats in [0, 1], named `*_ratio` or `*_prob`.
3. **Versioning:** All paths are prefixed `/api/v1/`.
4. **Error responses:** Uniform error envelope `{"error": {"code": "...", "message": "...", "details": []}}`.
