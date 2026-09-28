"""
REAL LOGIC — All tunable constants for the CyRIS risk engine.

This is the single source of truth for every numeric parameter used in
the Monte Carlo simulation, loss model, and frequency model.  Every
constant is documented with its rationale.
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────
# GENERAL
# ─────────────────────────────────────────────────────────

# Fixed "as_of" date for the synthetic dataset
AS_OF_DATE_ISO = "2026-09-28"

# Seed used by the default generation run
DEFAULT_SEED = 42

# ─────────────────────────────────────────────────────────
# LOSS MODEL — SLE six-component lookup tables
# All values are in integer INR.
# L (lakh) = 100_000 INR
# ─────────────────────────────────────────────────────────

L: int = 100_000  # shorthand: 1 lakh

# Hours of downtime per incident, keyed by asset criticality (1–5)
DOWNTIME_HOURS: dict[int, int] = {1: 1, 2: 2, 3: 4, 4: 6, 5: 8}

# Breach cost per incident, keyed by data_sensitivity (1–5)
BREACH_COST: dict[int, int] = {
    1: 1 * L,
    2: 4 * L,
    3: 12 * L,
    4: 30 * L,
    5: 60 * L,
}

# Recovery cost per incident, keyed by criticality (1–5)
RECOVERY_COST: dict[int, int] = {
    1: 0 * L + 50_000,   # 0.5 L
    2: 2 * L,
    3: 6 * L,
    4: 20 * L,
    5: 45 * L,
}

# Regulatory penalty (SEBI/RBI/DPDP Act), keyed by data_sensitivity (1–5)
REGULATORY_PENALTY: dict[int, int] = {
    1: 0,
    2: 0,
    3: 5 * L,
    4: 25 * L,
    5: 50 * L,
}

# Operational cost per incident, keyed by criticality (1–5)
OPERATIONAL_COST: dict[int, int] = {
    1: 0,
    2: 1 * L,
    3: 5 * L,
    4: 15 * L,
    5: 35 * L,
}

# Reputation cost per incident, keyed by criticality (1–5)
REPUTATION_COST: dict[int, int] = {
    1: 0,
    2: 0 * L + 50_000,  # 0.5 L
    3: 3 * L,
    4: 10 * L,
    5: 20 * L,
}

# ─────────────────────────────────────────────────────────
# FREQUENCY MODEL
# ─────────────────────────────────────────────────────────

# Baseline annual attempt rate.  This is the main calibration knob.
# Represents the expected number of serious attack campaigns
# targeting any given reachable asset per year.
ATTEMPT_RATE: float = 0.5

# Floor for p_comp — even an asset with zero open vulns has some
# residual risk from credential stuffing, misconfiguration, etc.
BASELINE_COMPROMISE_FLOOR: float = 0.01

# ─────────────────────────────────────────────────────────
# MONTE CARLO
# ─────────────────────────────────────────────────────────

# Default number of simulation iterations
DEFAULT_N_ITERATIONS: int = 10_000

# Maximum Poisson events per asset per year.
# The Poisson-via-exponential construction requires a ceiling.
MAX_EVENTS_PER_YEAR: int = 64

# Lognormal sigma for per-event loss variation.
# Higher → heavier tail.  Constrained to [0.6, 1.0] by spec.
LOSSMAG_SIGMA: float = 0.8

# Minimum required iterations (guardrail)
MIN_ITERATIONS: int = 1_000

# ─────────────────────────────────────────────────────────
# HISTOGRAM / EXCEEDANCE outputs
# ─────────────────────────────────────────────────────────

HISTOGRAM_BINS: int = 50
EXCEEDANCE_POINTS: int = 40

# ─────────────────────────────────────────────────────────
# DELAY-PATCH mutation assumption
# ─────────────────────────────────────────────────────────

# For each day a patch is delayed, exploitability is multiplied by
#   min(1 + DELAY_FACTOR * days, DELAY_CAP)
# Documented assumption in MODEL.md.
DELAY_FACTOR: float = 0.005
DELAY_CAP: float = 1.5
DELAY_EXPLOIT_CEIL: float = 0.99

# ─────────────────────────────────────────────────────────
# PHASE 3 — FASTAPI & TWINSTORE CONFIGURATION
# ─────────────────────────────────────────────────────────
import os

API_PREFIX: str = "/api/v1"
CYRIS_SEED: int = int(os.getenv("CYRIS_SEED", "42"))
CYRIS_N_ITERATIONS: int = int(os.getenv("CYRIS_N_ITERATIONS", "10000"))
CORS_ORIGINS: list[str] = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if o.strip()
]
SIM_CONCURRENCY: int = 2
RESULT_CACHE_SIZE: int = 64
TREND_BACKFILL_DAYS: int = 30
TREND_BACKFILL_STEP_DAYS: int = 3

# ─────────────────────────────────────────────────────────
# PHASE 4 — ATTACK PATH & BLAST RADIUS CONFIGURATION
# ─────────────────────────────────────────────────────────
BLAST_MIN_REACH: float = 0.02

# Suggested control mapping table for chokepoints
CHOKEPOINT_SUGGESTED_CONTROLS: dict[str, tuple[str, str]] = {
    "network_access": ("CTL-003", "API Gateway Web Application Firewall (WAF)"),
    "trust_relationship": ("CTL-010", "Zero-Trust IAM Policy Engine"),
    "credential_reuse": ("CTL-001", "Phishing-Resistant MFA Enforcement"),
    "token_hijack": ("CTL-007", "Privileged Access Management (PAM) Vaulting"),
    "service_call": ("CTL-002", "Strict Subnet Micro-Segmentation"),
    "data_flow": ("CTL-006", "Database Vault & HSM Field-Level Encryption"),
}

# ─────────────────────────────────────────────────────────
# PHASE 5 — WHAT-IF & COUNTERFACTUAL CONFIGURATION
# ─────────────────────────────────────────────────────────
PATCH_COST_PER_VULN_INR: int = 40_000        # ₹0.4 L per patched vulnerability
EDGE_SEVERANCE_COST_INR: int = 200_000       # ₹2 L per severed exploit edge
WHATIF_MAX_MUTATIONS: int = 10
WHATIF_N_MIN: int = 2_000
WHATIF_N_MAX: int = 50_000
COUNTERFACTUAL_SCREEN_TOP_M: int = 10
COUNTERFACTUAL_RETURN_TOP_K: int = 6

# ─────────────────────────────────────────────────────────
# PHASE 6 — BUDGET OPTIMIZER CONFIGURATION
# ─────────────────────────────────────────────────────────
OPTIMIZER_MAX_BUDGET_INR: int = 10_000_000   # ₹1 Cr; ASSUMPTION: max slider budget cap
OPTIMIZER_SWEEP_STEP_INR: int = 500_000      # ₹5 L curve resolution; ASSUMPTION: sweep step
OPTIMIZER_EXACT_MAX_OPTIONS: int = 14
OPTIMIZER_EXACT_TIME_BUDGET_S: float = 60.0
PATCH_TIERS: dict[str, tuple[float, float]] = {
    "critical": (9.0, 10.01),
    "high": (7.0, 9.0),
    "medium": (4.0, 7.0),
}




