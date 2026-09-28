"""
REAL LOGIC — Budget Optimizer Option Catalog.

Builds atomic purchasable options from candidate controls and disjoint vulnerability patch tiers.
Computes standalone analytic EAL reduction for each candidate option and filters out no-gain options.
"""
from __future__ import annotations

import copy
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.config import PATCH_COST_PER_VULN_INR, PATCH_TIERS
from app.decision.costing import cost_of
from app.risk.attack_paths import analytic_eal
from app.twin.engine import TwinEngine


class Option(BaseModel):
    """An atomic purchasable security action (control deployment or patch tier)."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique option identifier (canonical sorted key)")
    kind: str = Field(..., description="'control' | 'patch'")
    label: str = Field(..., description="Human-readable title/description")
    mutations: list[dict[str, Any]] = Field(..., description="List of mutations applied by option")
    cost_inr: int = Field(..., ge=0, description="Purchase/implementation cost in integer INR")
    standalone_gain_inr: float = Field(..., description="Analytic EAL reduction when applied alone")


class DroppedOption(BaseModel):
    """An option evaluated but excluded due to non-positive risk reduction."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(...)
    kind: str = Field(...)
    label: str = Field(...)
    cost_inr: int = Field(...)
    standalone_gain_inr: float = Field(...)
    reason: str = Field(...)


def build_options(twin: TwinEngine) -> tuple[list[Option], list[DroppedOption]]:
    """REAL LOGIC. Construct candidate option catalog from live twin.
    
    Returns (active_options, dropped_options) sorted canonically by option id.
    """
    base_eal = analytic_eal(twin)
    active_options: list[Option] = []
    dropped_options: list[DroppedOption] = []

    # 1. Control Options (candidate controls)
    candidate_controls = [c for c in twin.dataset.controls if c.status == "candidate"]
    for ctrl in candidate_controls:
        opt_id = ctrl.id
        muts = [{"type": "deploy_control", "control_id": ctrl.id}]
        cost_breakdown = cost_of(twin, muts)
        cost = cost_breakdown.total_inr

        # Evaluate standalone gain on cloned twin
        clone = TwinEngine(copy.deepcopy(twin.dataset))
        clone.toggle_control(ctrl.id, deployed=True)
        clone_eal = analytic_eal(clone)
        gain = base_eal - clone_eal

        opt = Option(
            id=opt_id,
            kind="control",
            label=ctrl.name,
            mutations=muts,
            cost_inr=cost,
            standalone_gain_inr=round(gain, 2),
        )

        if gain > 0:
            active_options.append(opt)
        else:
            dropped_options.append(
                DroppedOption(
                    id=opt_id,
                    kind="control",
                    label=ctrl.name,
                    cost_inr=cost,
                    standalone_gain_inr=round(gain, 2),
                    reason="Standalone analytic EAL reduction is zero or negative",
                )
            )

    # 2. Patch Tier Options
    vulns = twin.dataset.vulnerabilities
    for tier_key in ["critical", "high", "medium"]:
        if tier_key not in PATCH_TIERS:
            continue
        lo, hi = PATCH_TIERS[tier_key]
        tier_vulns = [
            v for v in vulns
            if v.patch_status != "patched" and lo <= v.cvss_score < hi
        ]
        if not tier_vulns:
            continue

        opt_id = f"PATCH-{tier_key.upper()}"
        v_ids = [v.id for v in tier_vulns]
        muts = [{"type": "patch_vulnerabilities", "vulnerability_ids": v_ids}]
        cost_breakdown = cost_of(twin, muts)
        cost = cost_breakdown.total_inr

        # Verify cost matches PATCH_COST_PER_VULN_INR * count
        expected_cost = len(v_ids) * PATCH_COST_PER_VULN_INR
        assert cost == expected_cost, f"Cost mismatch for {opt_id}: {cost} != {expected_cost}"


        # Evaluate standalone gain
        clone = TwinEngine(copy.deepcopy(twin.dataset))
        for vid in v_ids:
            clone.patch_vulnerability(vid)
        clone_eal = analytic_eal(clone)
        gain = base_eal - clone_eal

        tier_label = f"Patch All {tier_key.capitalize()} Vulnerabilities ({len(v_ids)})"

        opt = Option(
            id=opt_id,
            kind="patch",
            label=tier_label,
            mutations=muts,
            cost_inr=cost,
            standalone_gain_inr=round(gain, 2),
        )

        if gain > 0:
            active_options.append(opt)
        else:
            dropped_options.append(
                DroppedOption(
                    id=opt_id,
                    kind="patch",
                    label=tier_label,
                    cost_inr=cost,
                    standalone_gain_inr=round(gain, 2),
                    reason="Standalone analytic EAL reduction is zero or negative",
                )
            )

    # Sort canonically by option id
    active_options.sort(key=lambda o: o.id)
    dropped_options.sort(key=lambda o: o.id)

    return active_options, dropped_options
