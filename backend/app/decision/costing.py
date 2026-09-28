"""
REAL LOGIC — Financial Cost Model, ROSI, and Payback Calculator.

Calculates investment outlays, net risk reductions, Return on Security Investment (ROSI),
and capital payback periods for what-if security interventions.
"""
from __future__ import annotations

import dataclasses
from typing import Any

from app.config import EDGE_SEVERANCE_COST_INR, PATCH_COST_PER_VULN_INR
from app.twin.engine import TwinEngine


@dataclasses.dataclass
class CostItem:
    label: str
    amount_inr: int


@dataclasses.dataclass
class CostBreakdown:
    items: list[CostItem]
    total_inr: int


def cost_of(twin_before: TwinEngine, mutations: list[dict[str, Any]]) -> CostBreakdown:
    """Calculate total financial outlay cost and breakdown for a sequence of mutations."""
    items: list[CostItem] = []
    total = 0

    for mut in mutations:
        m_type = mut.get("type") or mut.get("action")

        if m_type == "deploy_control":
            cid = mut.get("control_id") or mut.get("controlId")
            ctrl = twin_before.control_map.get(cid) if cid else None
            if ctrl:
                subset = mut.get("asset_ids")
                if subset and len(ctrl.covered_asset_ids) > 0:
                    cost = int(ctrl.cost_inr * (len(subset) / float(len(ctrl.covered_asset_ids))))
                    label = f"Deploy {ctrl.name} on {len(subset)} assets"
                else:
                    cost = ctrl.cost_inr
                    label = f"Deploy {ctrl.name}"
                items.append(CostItem(label=label, amount_inr=cost))
                total += cost

        elif m_type in ("patch_vulnerability", "patch_vulnerabilities"):
            vid = mut.get("vulnerability_id") or mut.get("vulnId")
            vids = mut.get("vulnerability_ids") or mut.get("vulnIds")
            min_cvss = mut.get("min_cvss")
            asset_id = mut.get("asset_id")

            if vid:
                v_obj = twin_before.vuln_map.get(vid)
                if v_obj and v_obj.patch_status != "patched":
                    cost = PATCH_COST_PER_VULN_INR
                    items.append(CostItem(label=f"Patch {v_obj.cve_id}", amount_inr=cost))
                    total += cost
            elif vids:
                unpatched = [
                    v_id for v_id in vids
                    if v_id in twin_before.vuln_map and twin_before.vuln_map[v_id].patch_status != "patched"
                ]
                if unpatched:
                    cost = len(unpatched) * PATCH_COST_PER_VULN_INR
                    items.append(CostItem(label=f"Patch {len(unpatched)} open vulnerabilities", amount_inr=cost))
                    total += cost
            elif min_cvss is not None or asset_id is not None:
                matched = [
                    v for v in twin_before.dataset.vulnerabilities
                    if v.patch_status != "patched"
                    and (min_cvss is None or v.cvss_score >= min_cvss)
                    and (asset_id is None or v.asset_id == asset_id)
                ]
                if matched:
                    cost = len(matched) * PATCH_COST_PER_VULN_INR
                    items.append(CostItem(label=f"Patch {len(matched)} open vulnerabilities", amount_inr=cost))
                    total += cost


        elif m_type in ("remove_edge", "scale_edge_probability"):
            src = mut.get("source") or mut.get("src")
            tgt = mut.get("target") or mut.get("tgt")
            cost = EDGE_SEVERANCE_COST_INR
            items.append(CostItem(label=f"Sever exploit edge ({src} -> {tgt})", amount_inr=cost))
            total += cost

        # Zero-cost mutations (savings/side-effects not modeled)
        # remove_control, set_control_health, delay_patch, add_vulnerability

    return CostBreakdown(items=items, total_inr=total)


def compute_financial_metrics(
    eal_before: int,
    eal_after: int,
    cost_inr: int,
) -> tuple[int, float, float | None, float | None]:
    """Compute reduction_inr, delta_ratio, ROSI, and payback_months."""
    reduction_inr = eal_before - eal_after
    delta_ratio = round((eal_after - eal_before) / float(max(1, eal_before)), 4)

    if cost_inr > 0:
        rosi = round((reduction_inr - cost_inr) / float(cost_inr), 2)
    else:
        rosi = None

    if reduction_inr > 0 and cost_inr > 0:
        payback_months = round(cost_inr / (reduction_inr / 12.0), 1)
    else:
        payback_months = None

    return reduction_inr, delta_ratio, rosi, payback_months
