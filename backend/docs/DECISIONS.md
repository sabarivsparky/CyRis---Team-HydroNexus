# Design Decisions Log

> Every assumption, default, and naming mismatch is recorded here.
> Format: **D-NNN** — short title — rationale.

---

## Phase 0 — API Contract

**D-001** — Frontend field names take precedence over blueprint names.
The frontend is already built. Where the frontend uses a different name than the
blueprint (e.g. `eal` vs `eal_inr`, `share` vs `share_ratio`), the backend
schema includes *both* names: the backend-canonical `*_inr` / `*_ratio` fields
as the source of truth, plus frontend-compat aliases. This avoids touching any
frontend code.

**D-002** — `RiskContributor` naming mismatch.
Blueprint uses `eal_inr` and `share_ratio`. Frontend uses `eal` (integer INR)
and `share` (float 0–1). Backend schema carries both pairs. The backend will
populate both on serialization.

**D-003** — `TrendPoint` naming mismatch.
Blueprint uses `timestamp` + `eal_inr`. Frontend uses `label` (month name) +
`eal` (integer INR). Schema carries all four fields.

**D-004** — `AttackPath` dual field sets.
Blueprint uses `nodes`, `steps`, `path_probability`, `blast_radius_eal_inr`.
Frontend uses `nodeIds`, `edgeIds`, `ealContribution`, `hopsToCrownJewel`.
Schema carries both.

**D-005** — `CounterfactualCard` naming.
Blueprint: `action`, `eal_before_inr`, `eal_after_inr`. Frontend:
`proposedAction`, `controlId`. Schema carries both.

**D-006** — `OptimizerResult` dual fields.
Blueprint uses `selected_control_ids`, `total_cost_inr`, `eal_reduction_inr`.
Frontend uses `selectedIds`, `estimatedCost`, `riskReduction`, `resultingEal`,
`rosi`, `remainingBudget`. Schema carries both.

**D-007** — `TelemetryEvent` dual fields.
Backend-canonical: `event_type`, `message`, `eal_after_inr`. Frontend:
`event`, `source`, `severity`, `ealImpact`, `status`. Both present in schema.

**D-008** — `SecurityControl` (frontend) vs `Control` (backend).
The frontend `SecurityControl` type has fields (`description`, `cost`,
`standaloneReduction`, `blocksNodeIds`, `relatedPathId`, `frameworkHints`) that
differ from the backend `Control` schema. The backend is the authority for
the control data model (with `cost_inr`, `effectiveness`,
`impact_reduction`, `dampens_edge_types`, `covered_asset_ids`, `status`,
`health`). Phase 3 will map between them in the API layer.

**D-009** — `DashboardSnapshot` is a frontend-only composite.
`CyrisContext` builds it client-side from `riskService.getDashboard()`. The
backend provides the individual pieces (`/risk/summary`, `/risk/contributors`,
`/risk/trend`) rather than one monolith endpoint, because the data comes from
different computations. Documented but not a mismatch — the frontend can
assemble it.

**D-010** — `TwinGraphNode` extra fields.
Backend adds `is_crown_jewel`, `on_active_path`, and `eal_inr` to the node
shape. These are not in the frontend `GraphNode` type but are needed for
backend-driven rendering. Frontend can ignore unknown fields on its side
(though our Pydantic model uses `extra="forbid"` for the *backend's* own
validation).

---

## Phase 1 — Synthetic Data & Twin

**D-011** — `annual_revenue_dependency_inr` ranges use log-uniform draw.
Criticality 1: ₹0–50 L, 2: ₹50 L–5 Cr, 3: ₹5–50 Cr, 4: ₹50–300 Cr,
5: ₹300–2000 Cr. Log-uniform means `exp(uniform(ln(low), ln(high)))`,
floored to integer INR. For criticality 1 the lower bound is set to ₹1 L
(₹100,000) to avoid near-zero values that would make the asset irrelevant.

**D-012** — Generated asset names are hand-picked for realism.
The 20 non-hardcoded assets use a curated list of plausible Tier-1 bank asset
names rather than random strings.

**D-013** — `delay_patch` mutation multiplier.
exploitability ← exploitability × min(1 + 0.005 × days, 1.5), capped at 0.99.
This is a rough heuristic — real-world exploit probability growth is
non-linear and varies by CVE. Documented in MODEL.md.

**D-014** — Control `covers` resolution.
Controls specify coverage by asset type or subnet in the spec table. At
generation time, `covered_asset_ids` is resolved to concrete asset IDs
matching those criteria.

---

## Phase 2 — Monte Carlo Engine

*(To be filled as Phase 2 decisions are made.)*
