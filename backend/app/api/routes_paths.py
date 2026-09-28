"""
REAL LOGIC — Attack Paths, Chokepoint Recommendations & Asset Inspector Routes.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_store
from app.risk.attack_paths import (
    active_path,
    chokepoints,
    most_likely_paths,
)
from app.schemas import AttackPath, AttackPathStep
from app.state import TwinStore

router = APIRouter()


@router.get("/attack-paths", response_model=list[AttackPath])
def get_attack_paths_route(
    target: str | None = Query(None, description="Target asset ID"),
    source: str = Query("INTERNET", description="Source node ID"),
    k: int = Query(3, ge=1, le=10, description="Max paths to return (1-10)"),
    store: TwinStore = Depends(get_store),
) -> list[AttackPath]:
    """Return ranked attack paths from source to target (or top path per crown jewel if target omitted)."""
    twin = store.live_twin()
    act_path = active_path(twin)
    active_nodes = set(act_path.nodes) if act_path else set()

    results: list[AttackPath] = []

    if target:
        if target not in twin.asset_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target asset '{target}' not found.",
            )
        path_results = most_likely_paths(twin, target=target, source=source, k=k)
    else:
        # Top path per crown jewel
        crown_jewels = [a.id for a in twin.dataset.assets if a.is_crown_jewel or a.criticality == 5]
        path_results = []
        for cj in crown_jewels:
            p_res = most_likely_paths(twin, target=cj, source=source, k=1)
            path_results.extend(p_res)
        path_results.sort(key=lambda pr: pr.path_probability, reverse=True)
        path_results = path_results[:k]

    for idx, pr in enumerate(path_results, start=1):
        steps = [
            AttackPathStep(
                source=h.source,
                target=h.target,
                technique=h.relationship_type,
                probability=h.hop_probability,
            )
            for h in pr.hops
        ]
        edge_ids = [f"e-{h.source.lower()}-{h.target.lower()}" for h in pr.hops]
        frontend_nodes = [f"n-{n.lower()}" for n in pr.nodes]

        src_name = twin.asset_map[pr.nodes[1]].name if len(pr.nodes) > 1 and pr.nodes[1] in twin.asset_map else pr.nodes[0]
        tgt_name = twin.asset_map[pr.nodes[-1]].name if pr.nodes[-1] in twin.asset_map else pr.nodes[-1]

        results.append(
            AttackPath(
                id=f"path-{idx}",
                name=f"Attack Path #{idx} — {src_name} to {tgt_name}",
                nodes=pr.nodes,
                steps=steps,
                path_probability=pr.path_probability,
                blast_radius_eal_inr=pr.blast_radius_eal_inr,
                nodeIds=frontend_nodes,
                edgeIds=edge_ids,
                ealContribution=pr.blast_radius_eal_inr,
                hopsToCrownJewel=len(pr.nodes) - 1,
            )
        )

    return results


@router.get("/attack-paths/chokepoints")
def get_chokepoints_route(
    limit: int = Query(5, ge=1, le=20, description="Max chokepoints to return"),
    store: TwinStore = Depends(get_store),
) -> list[dict[str, Any]]:
    """Return ranked chokepoint edge severance recommendations."""
    twin = store.live_twin()
    cps = chokepoints(twin, limit=limit)

    return [
        {
            "source": cp.source,
            "target": cp.target,
            "relationship_type": cp.relationship_type,
            "eal_drop_inr": cp.eal_drop_inr,
            "suggested_control_id": cp.suggested_control_id,
            "suggested_control_name": cp.suggested_control_name,
            "control_already_deployed": cp.control_already_deployed,
        }
        for cp in cps
    ]


@router.get("/assets/{asset_id}")
def get_asset_detail_route(
    asset_id: str,
    store: TwinStore = Depends(get_store),
) -> dict[str, Any]:
    """Return asset inspector detail (asset properties, risk metrics, open vulns, controls, path_from_internet, path_to_crown_jewel)."""
    twin = store.live_twin()
    asset = twin.asset_map.get(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id}' not found.",
        )

    sim_res = store.baseline()
    a_risk = next((ar for ar in sim_res.assets if ar.asset_id == asset_id), None)

    # Open vulnerabilities
    open_vulns = [
        {
            "id": v.id,
            "cve_id": v.cve_id,
            "title": v.title,
            "cvss_score": v.cvss_score,
            "exploitability": v.exploitability,
            "category": v.category,
            "patch_status": v.patch_status,
        }
        for v in twin.dataset.vulnerabilities
        if v.asset_id == asset_id and v.patch_status != "patched"
    ]

    # Covering controls
    covering_controls = [
        {
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "effectiveness": c.effectiveness,
            "status": c.status,
            "health": c.health,
        }
        for c in twin.dataset.controls
        if asset_id in c.covered_asset_ids
    ]

    # Best path from internet to asset
    path_from_internet = most_likely_paths(twin, target=asset_id, source="INTERNET", k=1)
    path_from_internet_data = (
        {
            "nodes": path_from_internet[0].nodes,
            "path_probability": path_from_internet[0].path_probability,
            "hops": len(path_from_internet[0].nodes) - 1,
        }
        if path_from_internet
        else None
    )

    # Best path from asset to highest-risk reachable crown jewel
    crown_jewels = [a.id for a in twin.dataset.assets if (a.is_crown_jewel or a.criticality == 5) and a.id != asset_id]
    best_cj_path: dict[str, Any] | None = None
    best_cj_prob = -1.0

    for cj in crown_jewels:
        cj_paths = most_likely_paths(twin, target=cj, source=asset_id, k=1)
        if cj_paths and cj_paths[0].path_probability > best_cj_prob:
            best_cj_prob = cj_paths[0].path_probability
            best_cj_path = {
                "target_crown_jewel": cj,
                "nodes": cj_paths[0].nodes,
                "path_probability": cj_paths[0].path_probability,
                "hops": len(cj_paths[0].nodes) - 1,
            }

    return {
        "asset": asset.model_dump(mode="json"),
        "risk": a_risk.model_dump(mode="json") if a_risk else None,
        "vulnerabilities": open_vulns,
        "controls": covering_controls,
        "path_from_internet": path_from_internet_data,
        "path_to_crown_jewel": best_cj_path,
    }
