"""
REAL LOGIC — Attack Graph Analysis, Blast Radius, Chokepoint & Path Engine.

Builds exploit-only networkx graph, computes shortest simple paths, path risk scores,
chained blast radius EAL, weighted betweenness centrality, and chokepoint ranking.
"""
from __future__ import annotations

import copy
import dataclasses
import itertools
import math
import networkx as nx

from app.config import ATTEMPT_RATE, BLAST_MIN_REACH, CHOKEPOINT_SUGGESTED_CONTROLS
from app.risk.engine import compute_aro, compute_sle
from app.schemas import Asset, AttackPath, AttackPathStep, Control, Dataset
from app.twin.engine import TwinEngine


@dataclasses.dataclass
class Hop:
    source: str
    target: str
    relationship_type: str
    technique: str
    hop_probability: float


@dataclasses.dataclass
class PathResult:
    nodes: list[str]
    hops: list[Hop]
    path_probability: float
    path_risk_score_inr: float
    blast_radius_eal_inr: int
    blast_radius_asset_ids: list[str]


@dataclasses.dataclass
class Chokepoint:
    source: str
    target: str
    relationship_type: str
    eal_drop_inr: int
    suggested_control_id: str | None
    suggested_control_name: str | None
    control_already_deployed: bool


def _get_asset_pcomp(asset_id: str, twin: TwinEngine) -> float:
    """Return compromise probability p_comp(u) for an asset node."""
    if asset_id == "INTERNET":
        return 1.0
    asset = twin.asset_map.get(asset_id)
    if not asset:
        return 0.01
    aro = compute_aro(asset, twin.dataset)
    return min(1.0, max(0.01, aro / ATTEMPT_RATE))


def build_attack_graph(twin: TwinEngine) -> nx.DiGraph:
    """Build directed attack graph containing ONLY exploit edges (never protects edges)."""
    G = nx.DiGraph()

    # Add INTERNET node
    G.add_node("INTERNET", is_crown_jewel=False, criticality=1)

    # Add Asset nodes
    for asset in twin.dataset.assets:
        G.add_node(
            asset.id,
            name=asset.name,
            asset_type=asset.asset_type,
            criticality=asset.criticality,
            is_crown_jewel=asset.is_crown_jewel,
            subnet=asset.subnet,
        )

    # Add Exploit edges with logarithmic hop weight w = -ln(p_eff * p_comp(u))
    for edge in twin.dataset.edges:
        p_eff = twin._get_effective_edge_probability(edge)
        p_comp_u = _get_asset_pcomp(edge.source, twin)
        p_hop = p_eff * p_comp_u

        # Omit near-zero probability edges (<= 1e-12)
        if p_hop <= 1e-12:
            continue

        w = -math.log(max(1e-12, p_hop))

        G.add_edge(
            edge.source,
            edge.target,
            p_eff=p_eff,
            p_comp_u=p_comp_u,
            p_hop=p_hop,
            relationship_type=edge.relationship_type,
            description=edge.description,
            w=w,
            edge_kind="exploit",
        )

    return G


def analytic_eal(twin: TwinEngine) -> float:
    """Compute fast deterministic expected annual loss expectation without Monte Carlo."""
    total = 0.0
    for asset in twin.dataset.assets:
        aro = compute_aro(asset, twin.dataset)
        sle = compute_sle(asset)
        total += aro * sle
    return total


def calculate_blast_radius(entry_asset_id: str, twin: TwinEngine) -> tuple[int, list[str]]:
    """Compute chained blast radius assets and total downstream EAL at stake."""
    attack_graph = build_attack_graph(twin)
    if entry_asset_id not in attack_graph:
        return 0, []

    blast_assets: list[str] = [entry_asset_id]
    total_eal = 0

    # Calculate reachability probabilities downstream from entry asset
    for target_asset in twin.dataset.assets:
        if target_asset.id == entry_asset_id:
            a_sle = compute_sle(target_asset)
            a_aro = compute_aro(target_asset, twin.dataset)
            total_eal += int(a_sle * a_aro)
            continue

        try:
            if nx.has_path(attack_graph, entry_asset_id, target_asset.id):
                path = nx.shortest_path(attack_graph, entry_asset_id, target_asset.id, weight="w")
                prob = 1.0
                for u, v in zip(path[:-1], path[1:]):
                    data = attack_graph.get_edge_data(u, v)
                    prob *= data.get("p_eff", 0.5)

                if prob >= BLAST_MIN_REACH:
                    blast_assets.append(target_asset.id)
                    a_sle = compute_sle(target_asset)
                    a_aro = compute_aro(target_asset, twin.dataset)
                    total_eal += int(a_sle * a_aro)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue

    return total_eal, blast_assets


def most_likely_paths(
    twin: TwinEngine,
    target: str,
    source: str = "INTERNET",
    k: int = 3,
) -> list[PathResult]:
    """Compute top-k shortest simple attack paths from source to target sorted by probability."""
    attack_graph = build_attack_graph(twin)
    if source not in attack_graph or target not in attack_graph:
        return []

    target_asset = twin.asset_map.get(target)
    if not target_asset:
        return []

    target_sle = compute_sle(target_asset)
    target_pcomp = _get_asset_pcomp(target, twin)

    results: list[PathResult] = []

    try:
        raw_paths = list(
            itertools.islice(
                nx.shortest_simple_paths(attack_graph, source, target, weight="w"),
                k,
            )
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    for path_nodes in raw_paths:
        hops: list[Hop] = []
        path_prob = 1.0

        for u, v in zip(path_nodes[:-1], path_nodes[1:]):
            edge_data = attack_graph.get_edge_data(u, v)
            p_eff = edge_data.get("p_eff", 0.5)
            p_comp_u = edge_data.get("p_comp_u", 1.0)
            hop_prob = p_eff * p_comp_u
            path_prob *= hop_prob

            hops.append(
                Hop(
                    source=u,
                    target=v,
                    relationship_type=edge_data.get("relationship_type", "network_access"),
                    technique=edge_data.get("description", "Pivot"),
                    hop_probability=round(hop_prob, 4),
                )
            )

        end_to_end_prob = path_prob * target_pcomp
        risk_score_inr = end_to_end_prob * target_sle

        # Entry asset is the first node after INTERNET (or source)
        entry_id = path_nodes[1] if len(path_nodes) > 1 else path_nodes[0]
        blast_eal, blast_ids = calculate_blast_radius(entry_id, twin)

        results.append(
            PathResult(
                nodes=path_nodes,
                hops=hops,
                path_probability=round(end_to_end_prob, 6),
                path_risk_score_inr=risk_score_inr,
                blast_radius_eal_inr=blast_eal,
                blast_radius_asset_ids=blast_ids,
            )
        )

    results.sort(key=lambda pr: pr.path_probability, reverse=True)
    return results


def active_path(twin: TwinEngine) -> PathResult | None:
    """Determine the active highlight attack path having highest path_risk_score_inr over all crown jewels."""
    crown_jewel_ids = [a.id for a in twin.dataset.assets if a.is_crown_jewel or a.criticality == 5]
    best_res: PathResult | None = None

    for cj_id in crown_jewel_ids:
        paths = most_likely_paths(twin, target=cj_id, source="INTERNET", k=1)
        if paths:
            top_p = paths[0]
            if not best_res or top_p.path_risk_score_inr > best_res.path_risk_score_inr:
                best_res = top_p

    return best_res


def chokepoints(twin: TwinEngine, limit: int = 5) -> list[Chokepoint]:
    """Identify and rank top structural chokepoint edges whose severance yields largest EAL reduction."""
    crown_jewels = [a.id for a in twin.dataset.assets if a.is_crown_jewel or a.criticality == 5]
    candidate_edges: set[tuple[str, str]] = set()

    for cj in crown_jewels:
        paths = most_likely_paths(twin, target=cj, source="INTERNET", k=3)
        for p in paths:
            for hop in p.hops:
                candidate_edges.add((hop.source, hop.target))

    before_eal = analytic_eal(twin)
    ranked: list[Chokepoint] = []

    for src, tgt in candidate_edges:
        twin_clone = TwinEngine(twin.dataset)

        # Sever the candidate edge
        twin_clone.dataset.edges = [
            e for e in twin_clone.dataset.edges if not (e.source == src and e.target == tgt)
        ]
        twin_clone._build_graph()

        after_eal = analytic_eal(twin_clone)
        eal_drop = max(0, int(before_eal - after_eal))

        # Determine edge relationship_type
        orig_edge = next((e for e in twin.dataset.edges if e.source == src and e.target == tgt), None)
        rel_type = orig_edge.relationship_type if orig_edge else "network_access"

        ctrl_spec = CHOKEPOINT_SUGGESTED_CONTROLS.get(rel_type, ("CTL-002", "Strict Subnet Micro-Segmentation"))
        pref_ctrl_id, pref_ctrl_name = ctrl_spec

        ctrl_obj = twin.control_map.get(pref_ctrl_id)
        is_deployed = (ctrl_obj.status == "deployed") if ctrl_obj else False

        # Fallback to candidate control if already deployed
        if is_deployed:
            alt_ctrl = next(
                (c for c in twin.dataset.controls if c.status == "candidate" and rel_type in c.dampens_edge_types),
                None,
            )
            if alt_ctrl:
                pref_ctrl_id = alt_ctrl.id
                pref_ctrl_name = alt_ctrl.name
                is_deployed = False

        ranked.append(
            Chokepoint(
                source=src,
                target=tgt,
                relationship_type=rel_type,
                eal_drop_inr=eal_drop,
                suggested_control_id=pref_ctrl_id,
                suggested_control_name=pref_ctrl_name,
                control_already_deployed=is_deployed,
            )
        )

    ranked.sort(key=lambda cp: cp.eal_drop_inr, reverse=True)
    return ranked[:limit]
