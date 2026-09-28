/**
 * REAL LOGIC — Feature flags and per-panel mock switches.
 * Set individual flags to false to connect panels directly to the live FastAPI backend.
 */

export const USE_MOCK = {
  riskSummary: false,      // Phase 3 — LIVE
  riskTrend: false,        // Phase 3 — LIVE
  contributors: false,     // Phase 3 — LIVE
  attackGraph: false,      // Phase 4 — LIVE
  controls: false,         // Phase 5 — LIVE
  counterfactuals: false,  // Phase 5 — LIVE
  agents: true,            // Phase 7 — MOCK
  compliance: true,        // Phase 8 — MOCK
  telemetry: true,         // Phase 9 — MOCK
}
