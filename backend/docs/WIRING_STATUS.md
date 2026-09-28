# CyRIS UI Panel Wiring Registry

> **Document Status:** Authoritative status table of every frontend UI panel, backend API endpoint, integration state (LIVE vs MOCK), and phase mapping.

---

## UI Panel Wiring Table

| UI Panel / Component | Backend Endpoint | Status | Phase | Notes |
| :--- | :--- | :---: | :---: | :--- |
| **Headline EAL & VaR Cards** (`EALHero.tsx`) | `GET /api/v1/risk/summary` | **LIVE** | 3 | Real Monte Carlo org EAL & 95% VaR served from TwinStore. |
| **Risk Trend Chart** (`RiskTrendChart.tsx`) | `GET /api/v1/risk/trend` | **LIVE** | 3 | Honest 30-day as-of vulnerability replay history served from disk cache. |
| **Top Risk Contributors** (`RiskContributors.tsx`) | `GET /api/v1/risk/contributors` | **LIVE** | 3 | Dynamic per-asset EAL attribution list sorted by impact descending. |
| **Digital Twin Risk Graph** (`RiskGraph.tsx`) | `GET /api/v1/twin/graph` | MOCK | 4 | Wired in Phase 4. |
| **Attack Path Step Panel** (`AttackPathPanel.tsx`) | `GET /api/v1/attack-paths` | MOCK | 4 | Wired in Phase 4. |
| **Chokepoint Recommendations** | `GET /api/v1/attack-paths/chokepoints` | MOCK | 4 | Wired in Phase 4. |
| **Node Inspector Drilldown** (`NodeInspector.tsx`) | `GET /api/v1/assets/{asset_id}` | MOCK | 4 | Wired in Phase 4. |
| **What-If Sandbox** (`WhatIfSandbox.tsx`) | `POST /api/v1/whatif` | MOCK | 5 | Wired in Phase 5. |
| **Counterfactual Cards** (`CounterfactualCards.tsx`) | `GET /api/v1/counterfactuals` | MOCK | 5 | Wired in Phase 5. |
| **Budget Optimizer** (`OptimizerPage.tsx`) | `POST /api/v1/optimizer/run` | MOCK | 6 | Wired in Phase 6. |
| **Multi-Agent Swarm Debate** (`AgentPanels.tsx`) | `POST /api/v1/agents/debate` | MOCK | 7 | Wired in Phase 7. |
| **Compliance Mapping Table** (`ComplianceTable.tsx`) | `GET /api/v1/compliance/mappings` | MOCK | 8 | Wired in Phase 8. |
| **Audit Trail Ledger** (`AuditTrailPage.tsx`) | `GET /api/v1/audit/records` | MOCK | 8 | Wired in Phase 8. |
| **Live Telemetry Timeline** (`TelemetryPage.tsx`) | `GET /api/v1/telemetry/events` | MOCK | 9 | Wired in Phase 9. |
| **Remediation PR Approval** | `POST /api/v1/remediations/approve` | MOCK | 10 | Wired in Phase 10. |
