"""
REAL LOGIC — Risk Quantification API Routes.

Exposes /risk/summary, /risk/contributors, and /risk/trend endpoints.
All CPU-bound route functions are plain `def` (not `async def`) so FastAPI executes
them safely within its worker threadpool.
"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_store
from app.schemas import RiskContributor, RiskSummary, TrendPoint
from app.state import TwinStore
from app.twin.engine import TwinEngine

router = APIRouter()


def vulnerability_contributions(twin: TwinEngine, store: TwinStore) -> list[RiskContributor]:
    """Calculate exact EAL attribution for every open vulnerability across the estate."""
    sim_res = store.baseline()
    org_eal = max(1, sim_res.org.eal_inr)
    asset_risk_map = {ar.asset_id: ar.eal_inr for ar in sim_res.assets}

    # Group open vulns by asset
    asset_vulns: dict[str, list] = {}
    for v in twin.dataset.vulnerabilities:
        if v.patch_status != "patched":
            asset_vulns.setdefault(v.asset_id, []).append(v)

    contribs: list[RiskContributor] = []
    for asset_id, vulns in asset_vulns.items():
        a_eal = asset_risk_map.get(asset_id, 0)
        total_exp = sum(v.exploitability for v in vulns)
        if total_exp <= 0:
            continue

        for v in vulns:
            v_eal = int(a_eal * (v.exploitability / total_exp))
            share = min(1.0, round(v_eal / float(org_eal), 4))
            severity = "critical" if v.cvss_score >= 9.0 else "high" if v.cvss_score >= 7.0 else "medium"

            contribs.append(
                RiskContributor(
                    id=v.id,
                    name=f"{v.cve_id} — {v.title}",
                    level="vulnerability",
                    eal_inr=v_eal,
                    share_ratio=share,
                    pathId="",
                    eal=v_eal,
                    share=share,
                    severity=severity, # type: ignore
                )
            )

    contribs.sort(key=lambda c: c.eal_inr, reverse=True)
    return contribs


@router.get("/risk/summary", response_model=RiskSummary)
def get_risk_summary_route(store: TwinStore = Depends(get_store)) -> RiskSummary:
    """Return organization-level risk summary for live twin."""
    sim_res = store.baseline()
    twin = store.live_twin()
    summary = RiskSummary(
        eal_inr=sim_res.org.eal_inr,
        var95_inr=sim_res.org.var95_inr,
        var99_inr=sim_res.org.var99_inr,
        cvar95_inr=sim_res.org.cvar95_inr,
        as_of=sim_res.meta.as_of,
        histogram=sim_res.org.histogram,
        exceedance_curve=sim_res.org.exceedance_curve,
    )
    # Additive twin_fingerprint field
    summary.__dict__["twin_fingerprint"] = store.get_fingerprint(twin)
    return summary


@router.get("/risk/contributors", response_model=list[RiskContributor])
def get_risk_contributors_route(
    level: str = Query("asset", description="Level: asset, vulnerability, or business_unit"),
    limit: int = Query(10, ge=1, le=100, description="Max items (1-100)"),
    store: TwinStore = Depends(get_store),
) -> list[RiskContributor]:
    """Return top risk contributors sorted by EAL descending."""
    if level not in ("asset", "vulnerability", "business_unit"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid level '{level}'. Must be one of: asset, vulnerability, business_unit.",
        )

    twin = store.live_twin()
    sim_res = store.baseline()
    org_eal = max(1, sim_res.org.eal_inr)

    if level == "vulnerability":
        contribs = vulnerability_contributions(twin, store)
    elif level == "business_unit":
        contribs = []
        for bu_risk in sim_res.business_units:
            share = min(1.0, round(bu_risk.eal_inr / float(org_eal), 4))
            sev = "critical" if share > 0.3 else "high" if share > 0.15 else "medium"
            contribs.append(
                RiskContributor(
                    id=f"bu-{bu_risk.business_unit.lower().replace(' ', '-')}",
                    name=bu_risk.business_unit,
                    level="business_unit",
                    eal_inr=bu_risk.eal_inr,
                    share_ratio=share,
                    pathId="",
                    eal=bu_risk.eal_inr,
                    share=share,
                    severity=sev, # type: ignore
                )
            )
        contribs.sort(key=lambda c: c.eal_inr, reverse=True)
    else:  # asset
        contribs = []
        for ar in sim_res.assets:
            share = min(1.0, round(ar.eal_inr / float(org_eal), 4))
            sev = "critical" if ar.eal_inr > org_eal * 0.2 else "high" if ar.eal_inr > org_eal * 0.1 else "medium"
            contribs.append(
                RiskContributor(
                    id=ar.asset_id,
                    name=ar.name,
                    level="asset",
                    eal_inr=ar.eal_inr,
                    share_ratio=share,
                    pathId="path-1" if "INTERNET" in ar.best_path else "",
                    eal=ar.eal_inr,
                    share=share,
                    severity=sev, # type: ignore
                )
            )
        contribs.sort(key=lambda c: c.eal_inr, reverse=True)

    return contribs[:limit]


@router.get("/risk/trend", response_model=list[TrendPoint])
def get_risk_trend_route(store: TwinStore = Depends(get_store)) -> list[TrendPoint]:
    """Return historical and live EAL trend points."""
    return store.trend.get_points()
