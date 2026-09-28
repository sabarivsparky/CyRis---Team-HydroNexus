"""
REAL LOGIC — Twin Graph Route.

Exposes /twin/graph with weighted betweenness centrality, active attack path highlighting,
and optional control nodes/edges.
"""
from __future__ import annotations

import networkx as nx
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_store
from app.risk.attack_paths import active_path, build_attack_graph
from app.schemas import TwinGraphEdge, TwinGraphNode, TwinGraphView
from app.state import TwinStore

router = APIRouter()


@router.get("/twin/graph", response_model=TwinGraphView)
def get_twin_graph_route(
    include_controls: bool = Query(True, description="Include control nodes and protects edges"),
    store: TwinStore = Depends(get_store),
) -> TwinGraphView:
    """Return enriched Digital Twin graph view for WebGL / D3 node mesh visualization."""
    twin = store.live_twin()
    attack_graph = build_attack_graph(twin)

    # Compute weighted betweenness centrality
    try:
        centrality = nx.betweenness_centrality(attack_graph, weight="w")
    except Exception:
        centrality = {a.id: 0.0 for a in twin.dataset.assets}

    # Active attack path highlighting
    act_path = active_path(twin)
    active_node_ids = set(act_path.nodes) if act_path else set()
    active_edge_pairs = (
        set(zip(act_path.nodes[:-1], act_path.nodes[1:])) if act_path else set()
    )

    nodes: list[TwinGraphNode] = []
    subnet_x = {"External": 50.0, "Subnet A": 200.0, "Subnet B": 550.0, "Subnet C": 900.0}
    subnet_counters = {"External": 0, "Subnet A": 0, "Subnet B": 0, "Subnet C": 0}

    # External INTERNET Node
    nodes.append(
        TwinGraphNode(
            id="n-internet",
            name="External Internet",
            type="external",
            criticality="nominal",
            ealContribution=0,
            status="monitored",
            x=50.0,
            y=250.0,
            dependencies=[],
            is_crown_jewel=False,
            on_active_path=("INTERNET" in active_node_ids),
            eal_inr=0,
        )
    )

    crit_str_map = {5: "critical", 4: "high", 3: "medium", 2: "low", 1: "nominal"}

    for asset in twin.dataset.assets:
        sub = asset.subnet if asset.subnet in subnet_x else "Subnet A"
        subnet_counters[sub] += 1
        y_pos = 80.0 + (subnet_counters[sub] * 70.0)
        x_pos = subnet_x[sub]

        if asset.is_crown_jewel or asset.criticality == 5:
            node_type = "crown-jewel"
        elif asset.asset_type == "identity":
            node_type = "identity"
        else:
            node_type = "asset"

        on_path = asset.id in active_node_ids
        status_val = "exposed" if (asset.is_crown_jewel and on_path) else "degraded" if on_path else "hardened"

        node_id = f"n-{asset.id.lower()}"
        deps = [f"n-{u.lower()}" for u, v in twin.graph.in_edges(asset.id)]

        node = TwinGraphNode(
            id=node_id,
            name=asset.name,
            type=node_type, # type: ignore
            criticality=crit_str_map.get(asset.criticality, "medium"), # type: ignore
            ealContribution=int(asset.annual_revenue_dependency_inr * 0.05),
            status=status_val, # type: ignore
            x=x_pos,
            y=y_pos,
            dependencies=deps,
            is_crown_jewel=asset.is_crown_jewel,
            on_active_path=on_path,
            eal_inr=int(asset.annual_revenue_dependency_inr * 0.05),
        )
        # Attach betweenness centrality dynamically
        node.__dict__["betweenness"] = round(centrality.get(asset.id, 0.0), 4)
        node.__dict__["internet_facing"] = asset.internet_facing
        node.__dict__["business_unit"] = asset.business_unit

        nodes.append(node)

    edges: list[TwinGraphEdge] = []
    for u, v, data in twin.graph.edges(data=True):
        edge_id = f"e-{u.lower()}-{v.lower()}"
        src_id = f"n-{u.lower()}"
        tgt_id = f"n-{v.lower()}"
        on_active = (u, v) in active_edge_pairs

        p_eff = data.get("exploit_probability", 0.5)
        label = f"{data.get('relationship_type', 'pivot')} ({int(p_eff * 100)}%)"

        edge = TwinGraphEdge(
            id=edge_id,
            source=src_id,
            target=tgt_id,
            kind="attack",
            label=label,
        )
        edge.__dict__["exploit_probability"] = data.get("base_probability", p_eff)
        edge.__dict__["effective_probability"] = p_eff
        edge.__dict__["relationship_type"] = data.get("relationship_type", "network_access")
        edge.__dict__["on_active_path"] = on_active

        edges.append(edge)

    # Optional control nodes and protects edges
    if include_controls:
        for idx, ctrl in enumerate(twin.dataset.controls, start=1):
            c_node_id = f"n-{ctrl.id.lower()}"
            c_status = "active" if ctrl.status == "deployed" else "proposed"

            nodes.append(
                TwinGraphNode(
                    id=c_node_id,
                    name=ctrl.name,
                    type="control",
                    criticality="medium",
                    ealContribution=0,
                    status=c_status, # type: ignore
                    x=400.0,
                    y=50.0 + (idx * 50.0),
                    dependencies=[],
                    is_crown_jewel=False,
                    on_active_path=False,
                    eal_inr=0,
                )
            )

            for target_asset_id in ctrl.covered_asset_ids:
                e_id = f"e-{ctrl.id.lower()}-{target_asset_id.lower()}"
                edge = TwinGraphEdge(
                    id=e_id,
                    source=c_node_id,
                    target=f"n-{target_asset_id.lower()}",
                    kind="control",
                    label=f"Protects ({ctrl.category})",
                )
                edge.__dict__["protects"] = True
                edges.append(edge)

    return TwinGraphView(nodes=nodes, edges=edges)
