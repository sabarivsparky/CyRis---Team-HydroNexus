"""
REAL LOGIC — Living Digital Twin Graph Analytics Engine.

Builds and maintains the attack-path network graph from synthetic datasets.
Computes multi-hop attack paths, shortest paths to crown jewels, network centrality,
and handles graph mutations (e.g. patching vulnerabilities, delaying patches, control toggling).
"""
from __future__ import annotations

import copy
import math
import networkx as nx

from app.config import DELAY_CAP, DELAY_EXPLOIT_CEIL, DELAY_FACTOR
from app.schemas import (
    Asset,
    AttackPath,
    AttackPathStep,
    Control,
    Dataset,
    ExploitEdge,
    TwinGraphEdge,
    TwinGraphNode,
    TwinGraphView,
    Vulnerability,
)


class TwinEngine:
    """Living Digital Twin Graph Engine wrapping NetworkX."""

    def __init__(self, dataset: Dataset):
        self.dataset = copy.deepcopy(dataset)
        self.asset_map: dict[str, Asset] = {a.id: a for a in self.dataset.assets}
        self.vuln_map: dict[str, Vulnerability] = {v.id: v for v in self.dataset.vulnerabilities}
        self.control_map: dict[str, Control] = {c.id: c for c in self.dataset.controls}
        self.graph = nx.DiGraph()
        self._build_graph()

    def _get_effective_edge_probability(self, edge: ExploitEdge) -> float:
        """Calculate effective probability of an exploit edge considering active controls."""
        prob = edge.exploit_probability

        # Find active deployed controls protecting source or target asset
        for control in self.dataset.controls:
            if control.status != "deployed":
                continue

            # Check if control covers either source or target asset
            is_covered = (edge.source in control.covered_asset_ids) or (edge.target in control.covered_asset_ids)
            if not is_covered:
                continue

            # Check if control dampens this relationship type
            if edge.relationship_type in control.dampens_edge_types:
                dampening = control.dampens_edge_types[edge.relationship_type]
                reduction = control.effectiveness * control.health * dampening
                prob *= (1.0 - reduction)

        return max(0.001, min(0.99, prob))

    def _build_graph(self) -> None:
        """Construct the NetworkX directed graph from dataset."""
        self.graph.clear()

        # Add INTERNET node
        self.graph.add_node(
            "INTERNET",
            name="External Internet",
            asset_type="external",
            criticality=1,
            is_crown_jewel=False,
            subnet="External",
        )

        # Add Asset nodes
        for asset in self.dataset.assets:
            self.graph.add_node(
                asset.id,
                name=asset.name,
                asset_type=asset.asset_type,
                criticality=asset.criticality,
                is_crown_jewel=asset.is_crown_jewel,
                subnet=asset.subnet,
                annual_revenue_dependency_inr=asset.annual_revenue_dependency_inr,
                data_sensitivity=asset.data_sensitivity,
                internet_facing=asset.internet_facing,
            )

        # Add Exploit edges
        for edge in self.dataset.edges:
            eff_prob = self._get_effective_edge_probability(edge)
            self.graph.add_edge(
                edge.source,
                edge.target,
                relationship_type=edge.relationship_type,
                exploit_probability=eff_prob,
                description=edge.description,
                base_probability=edge.exploit_probability,
            )

    def get_attack_paths(self, max_cutoff: int = 6) -> list[AttackPath]:
        """Discover and rank all attack paths from INTERNET / public ingress to crown jewels."""
        crown_jewel_ids = [a.id for a in self.dataset.assets if a.is_crown_jewel or a.criticality == 5]
        if not crown_jewel_ids:
            return []

        # Find ingress starting nodes (INTERNET or internet_facing assets)
        sources = ["INTERNET"] + [a.id for a in self.dataset.assets if a.internet_facing]
        raw_paths: list[tuple[list[str], float]] = []

        for src in sources:
            for target in crown_jewel_ids:
                if src == target:
                    continue
                try:
                    paths = list(nx.all_simple_paths(self.graph, source=src, target=target, cutoff=max_cutoff))
                    for path in paths:
                        # Ensure INTERNET path doesn't start with internet facing if INTERNET is first
                        if path[0] != "INTERNET" and "INTERNET" in path:
                            continue
                        
                        # Calculate end-to-end path probability
                        prob = 1.0
                        for u, v in zip(path[:-1], path[1:]):
                            edge_data = self.graph.get_edge_data(u, v)
                            prob *= edge_data.get("exploit_probability", 0.5)

                        raw_paths.append((path, prob))
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

        # Sort paths by probability descending
        raw_paths.sort(key=lambda item: item[1], reverse=True)

        # Remove duplicate node sequences
        unique_paths: list[tuple[list[str], float]] = []
        seen_seqs = set()
        for p, prob in raw_paths:
            seq_tuple = tuple(p)
            if seq_tuple not in seen_seqs:
                seen_seqs.add(seq_tuple)
                unique_paths.append((p, prob))

        attack_paths: list[AttackPath] = []
        for idx, (path_nodes, prob) in enumerate(unique_paths[:10], start=1):
            steps: list[AttackPathStep] = []
            edge_ids: list[str] = []

            for i in range(len(path_nodes) - 1):
                u, v = path_nodes[i], path_nodes[i + 1]
                edge_data = self.graph.get_edge_data(u, v)
                rel_type = edge_data.get("relationship_type", "network_access")
                step_prob = edge_data.get("exploit_probability", 0.5)

                steps.append(
                    AttackPathStep(
                        source=u,
                        target=v,
                        technique=rel_type,
                        probability=round(step_prob, 3),
                    )
                )
                edge_ids.append(f"e-{u}-{v}")

            # Calculate blast radius EAL in INR
            target_asset = self.asset_map.get(path_nodes[-1])
            target_rev = target_asset.annual_revenue_dependency_inr if target_asset else 100_000_000
            blast_radius_eal = int(target_rev * 0.15 * prob)

            # Node ID formatting for UI compatibility
            frontend_node_ids = [f"n-{n.lower()}" for n in path_nodes]

            src_name = self.asset_map[path_nodes[1]].name if len(path_nodes) > 1 and path_nodes[1] in self.asset_map else path_nodes[0]
            tgt_name = self.asset_map[path_nodes[-1]].name if path_nodes[-1] in self.asset_map else path_nodes[-1]
            path_name = f"Attack Path #{idx} — {src_name} to {tgt_name}"

            attack_paths.append(
                AttackPath(
                    id=f"path-{idx}",
                    name=path_name,
                    nodes=path_nodes,
                    steps=steps,
                    path_probability=round(prob, 4),
                    blast_radius_eal_inr=blast_radius_eal,
                    nodeIds=frontend_node_ids,
                    edgeIds=edge_ids,
                    ealContribution=blast_radius_eal,
                    hopsToCrownJewel=len(path_nodes) - 1,
                )
            )

        return attack_paths

    def get_shortest_path_to_crown_jewel(self, start_asset_id: str) -> list[str]:
        """Return shortest hop path from start asset to nearest crown jewel."""
        crown_jewels = [a.id for a in self.dataset.assets if a.is_crown_jewel or a.criticality == 5]
        shortest: list[str] = []

        for cj in crown_jewels:
            if start_asset_id == cj:
                return [start_asset_id]
            try:
                p = nx.shortest_path(self.graph, source=start_asset_id, target=cj)
                if not shortest or len(p) < len(shortest):
                    shortest = p
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

        return shortest

    def get_betweenness_centrality(self) -> dict[str, float]:
        """Compute betweenness centrality for all nodes in the asset graph."""
        return nx.betweenness_centrality(self.graph, normalized=True)

    def get_twin_graph_view(self) -> TwinGraphView:
        """Generate structured graph view for Digital Twin visualization panel."""
        active_paths = self.get_attack_paths()
        active_nodes = set()
        for ap in active_paths:
            active_nodes.update(ap.nodes)

        nodes: list[TwinGraphNode] = []
        # Position mapping heuristics (Subnet A: x~150, Subnet B: x~500, Subnet C: x~850)
        subnet_x = {"External": 50.0, "Subnet A": 200.0, "Subnet B": 550.0, "Subnet C": 900.0}
        subnet_counters = {"External": 0, "Subnet A": 0, "Subnet B": 0, "Subnet C": 0}

        # Add External Node
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
                on_active_path=True,
                eal_inr=0,
            )
        )

        crit_str_map = {5: "critical", 4: "high", 3: "medium", 2: "low", 1: "nominal"}

        for asset in self.dataset.assets:
            sub = asset.subnet if asset.subnet in subnet_x else "Subnet A"
            subnet_counters[sub] += 1
            y_pos = 80.0 + (subnet_counters[sub] * 70.0)
            x_pos = subnet_x[sub]

            # Node type
            if asset.is_crown_jewel or asset.criticality == 5:
                node_type = "crown-jewel"
            elif asset.asset_type == "identity":
                node_type = "identity"
            else:
                node_type = "asset"

            # Status
            on_path = asset.id in active_nodes
            if asset.is_crown_jewel and on_path:
                status = "exposed"
            elif on_path:
                status = "degraded" if asset.internet_facing else "active"
            else:
                status = "hardened"

            crit_level = crit_str_map.get(asset.criticality, "medium")
            node_id = f"n-{asset.id.lower()}"

            # Compute dependencies (incoming edge sources)
            deps = [
                f"n-{u.lower()}"
                for u, v in self.graph.in_edges(asset.id)
            ]

            nodes.append(
                TwinGraphNode(
                    id=node_id,
                    name=asset.name,
                    type=node_type,
                    criticality=crit_level, # type: ignore
                    ealContribution=int(asset.annual_revenue_dependency_inr * 0.05),
                    status=status, # type: ignore
                    x=x_pos,
                    y=y_pos,
                    dependencies=deps,
                    is_crown_jewel=asset.is_crown_jewel,
                    on_active_path=on_path,
                    eal_inr=int(asset.annual_revenue_dependency_inr * 0.05),
                )
            )

        edges: list[TwinGraphEdge] = []
        for u, v, data in self.graph.edges(data=True):
            edge_id = f"e-{u.lower()}-{v.lower()}"
            src_id = f"n-{u.lower()}"
            tgt_id = f"n-{v.lower()}"
            label = f"{data.get('relationship_type', 'pivot')} ({int(data.get('exploit_probability', 0.5)*100)}%)"

            edges.append(
                TwinGraphEdge(
                    id=edge_id,
                    source=src_id,
                    target=tgt_id,
                    kind="attack",
                    label=label,
                )
            )

        return TwinGraphView(nodes=nodes, edges=edges)

    # ── Mutation Methods ──────────────────────────────────────

    def patch_vulnerability(self, vulnerability_id: str) -> TwinEngine:
        """Patch a vulnerability, reducing its exploitability to 0."""
        for v in self.dataset.vulnerabilities:
            if v.id == vulnerability_id:
                v.patch_status = "patched"
                v.exploitability = 0.0
                break
        self._build_graph()
        return self

    def delay_patch(self, vulnerability_id: str, days: int) -> TwinEngine:
        """Delay patching, increasing exploitability by delay multiplier."""
        for v in self.dataset.vulnerabilities:
            if v.id == vulnerability_id:
                factor = min(1.0 + DELAY_FACTOR * days, DELAY_CAP)
                v.exploitability = min(DELAY_EXPLOIT_CEIL, v.exploitability * factor)
                break
        self._build_graph()
        return self

    def toggle_control(self, control_id: str, deployed: bool) -> TwinEngine:
        """Toggle control status between deployed and candidate."""
        for c in self.dataset.controls:
            if c.id == control_id:
                c.status = "deployed" if deployed else "candidate"
                break
        self._build_graph()
        return self

    def add_control(self, control: Control) -> TwinEngine:
        """Add a new security control to the dataset."""
        self.dataset.controls.append(control)
        self.control_map[control.id] = control
        self._build_graph()
        return self
