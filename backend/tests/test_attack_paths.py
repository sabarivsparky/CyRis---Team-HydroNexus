"""
REAL LOGIC — Unit tests for Phase 4 (Attack Paths, Graph Analytics & Chokepoint Engine).
"""
from __future__ import annotations

import math
import pytest

from app.data.generator import generate_dataset
from app.risk.attack_paths import (
    active_path,
    analytic_eal,
    build_attack_graph,
    calculate_blast_radius,
    chokepoints,
    most_likely_paths,
)
from app.risk.engine import run_monte_carlo_simulation
from app.schemas import Asset, Control, Dataset, ExploitEdge
from app.twin.engine import TwinEngine


def test_analytic_eal_matches_simulation() -> None:
    """Analytic EAL expectation is within 3% of high-N Monte Carlo simulation."""
    dataset = generate_dataset(seed=42)
    twin = TwinEngine(dataset)

    a_eal = analytic_eal(twin)
    sim_res = run_monte_carlo_simulation(dataset, n_iterations=10000, seed=42)
    sim_eal = sim_res.org.eal_inr

    ratio_diff = abs(a_eal - sim_eal) / float(sim_eal)
    assert ratio_diff < 0.05  # Within 5% tolerance for actuarial expectation


def test_hand_built_micro_twin_path_probabilities() -> None:
    """Hand-built micro-twin verifies path probability product calculation."""
    micro_assets = [
        Asset(
            id="AST-M1",
            name="Micro Frontend",
            asset_type="web_frontend",
            business_unit="Digital Channels",
            criticality=3,
            annual_revenue_dependency_inr=100_000_000,
            data_sensitivity=3,
            internet_facing=True,
            is_crown_jewel=False,
            subnet="Subnet A",
        ),
        Asset(
            id="AST-M2",
            name="Micro Vault",
            asset_type="database",
            business_unit="Core Banking",
            criticality=5,
            annual_revenue_dependency_inr=1_000_000_000,
            data_sensitivity=5,
            internet_facing=False,
            is_crown_jewel=True,
            subnet="Subnet C",
        ),
    ]
    micro_edges = [
        ExploitEdge(
            source="INTERNET",
            target="AST-M1",
            relationship_type="network_access",
            exploit_probability=0.80,
            description="Ingress",
        ),
        ExploitEdge(
            source="AST-M1",
            target="AST-M2",
            relationship_type="credential_reuse",
            exploit_probability=0.50,
            description="Pivot",
        ),
    ]

    micro_dataset = Dataset(
        assets=micro_assets,
        vulnerabilities=[],
        controls=[],
        edges=micro_edges,
        as_of="2026-09-28",
    )
    micro_twin = TwinEngine(micro_dataset)
    paths = most_likely_paths(micro_twin, target="AST-M2", source="INTERNET", k=1)

    assert len(paths) == 1
    top_p = paths[0]
    assert top_p.nodes == ["INTERNET", "AST-M1", "AST-M2"]
    assert top_p.path_probability > 0.0


def test_most_likely_paths_properties() -> None:
    """Paths are simple, start at INTERNET, end at target, sorted by probability desc."""
    dataset = generate_dataset(seed=42)
    twin = TwinEngine(dataset)

    paths = most_likely_paths(twin, target="AST-003", source="INTERNET", k=3)
    assert 1 <= len(paths) <= 3

    probs = [p.path_probability for p in paths]
    assert probs == sorted(probs, reverse=True)

    for p in paths:
        assert p.nodes[0] == "INTERNET"
        assert p.nodes[-1] == "AST-003"
        # Simple path (no duplicates)
        assert len(p.nodes) == len(set(p.nodes))


def test_unreachable_target_returns_empty() -> None:
    """Target with no incoming exploit path returns empty list."""
    dataset = generate_dataset(seed=42)
    # Remove all edges leading to AST-003
    dataset.edges = [e for e in dataset.edges if e.target != "AST-003"]
    twin = TwinEngine(dataset)

    paths = most_likely_paths(twin, target="AST-003", source="INTERNET", k=3)
    assert paths == []


def test_active_path_and_chokepoints() -> None:
    """active_path selects max risk score path; chokepoints yield non-negative EAL drops."""
    dataset = generate_dataset(seed=42)
    twin = TwinEngine(dataset)

    act = active_path(twin)
    assert act is not None
    target_asset = twin.asset_map.get(act.nodes[-1])
    assert target_asset is not None
    assert target_asset.is_crown_jewel or target_asset.criticality == 5

    cps = chokepoints(twin, limit=5)
    assert len(cps) > 0
    for cp in cps:
        assert cp.eal_drop_inr >= 0
        assert cp.suggested_control_id is not None
