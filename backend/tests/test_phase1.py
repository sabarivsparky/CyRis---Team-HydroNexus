"""
REAL LOGIC — Unit tests for Phase 1 (Data Generator & Digital Twin Engine).
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.config import DEFAULT_SEED
from app.data.generator import generate_dataset, load_dataset, save_dataset
from app.schemas import Control, Dataset
from app.twin.engine import TwinEngine


def test_data_generator_determinism() -> None:
    """Same seed yields byte-identical JSON dataset output."""
    d1 = generate_dataset(seed=DEFAULT_SEED)
    d2 = generate_dataset(seed=DEFAULT_SEED)
    assert d1.model_dump_json() == d2.model_dump_json()


def test_dataset_structure_and_counts() -> None:
    """Dataset contains exactly 25 assets (5 core + 20 synthetic) and valid components."""
    dataset = generate_dataset(seed=42)
    assert len(dataset.assets) == 25
    assert len(dataset.vulnerabilities) >= 25
    assert len(dataset.controls) >= 10
    assert len(dataset.edges) >= 7

    # Verify hardcoded core assets
    ast1 = next(a for a in dataset.assets if a.id == "AST-001")
    assert ast1.name == "Mobile Banking API Front-End"
    assert ast1.internet_facing is True
    assert ast1.criticality == 3

    ast3 = next(a for a in dataset.assets if a.id == "AST-003")
    assert ast3.name == "Core Transaction Database Vault"
    assert ast3.is_crown_jewel is True
    assert ast3.criticality == 5


def test_dataset_persistence() -> None:
    """save_dataset and load_dataset roundtrip cleanly."""
    dataset = generate_dataset(seed=42)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "dataset.json"
        save_dataset(dataset, tmp_path)
        assert tmp_path.exists()

        loaded = load_dataset(tmp_path)
        assert loaded.model_dump() == dataset.model_dump()


def test_twin_engine_graph_construction() -> None:
    """TwinEngine builds graph and computes attack paths."""
    dataset = generate_dataset(seed=42)
    twin = TwinEngine(dataset)

    assert "INTERNET" in twin.graph.nodes
    assert "AST-001" in twin.graph.nodes
    assert "AST-003" in twin.graph.nodes

    paths = twin.get_attack_paths()
    assert len(paths) > 0

    # Ensure path 1 connects to a crown jewel
    first_path = paths[0]
    assert first_path.hopsToCrownJewel >= 1
    assert first_path.path_probability > 0.0


def test_twin_engine_shortest_path_and_centrality() -> None:
    """TwinEngine computes shortest path to crown jewel and betweenness centrality."""
    dataset = generate_dataset(seed=42)
    twin = TwinEngine(dataset)

    sp = twin.get_shortest_path_to_crown_jewel("AST-001")
    assert len(sp) >= 2
    assert sp[0] == "AST-001"

    centrality = twin.get_betweenness_centrality()
    assert isinstance(centrality, dict)
    assert "AST-001" in centrality


def test_twin_engine_graph_view() -> None:
    """get_twin_graph_view produces formatted graph layout."""
    dataset = generate_dataset(seed=42)
    twin = TwinEngine(dataset)
    graph_view = twin.get_twin_graph_view()

    assert len(graph_view.nodes) >= 26  # 25 assets + INTERNET
    assert len(graph_view.edges) >= 7

    node_ids = {n.id for n in graph_view.nodes}
    assert "n-internet" in node_ids
    assert "n-ast-001" in node_ids


def test_twin_engine_mutations() -> None:
    """Graph mutation methods dynamically update state and edge weights."""
    dataset = generate_dataset(seed=42)
    twin = TwinEngine(dataset)

    initial_paths = twin.get_attack_paths()
    initial_prob = initial_paths[0].path_probability

    # Deploy control protecting path assets
    twin.toggle_control("CTL-001", deployed=True)
    post_control_paths = twin.get_attack_paths()
    assert len(post_control_paths) > 0

    # Patch vulnerability CVE-2026-3827
    twin.patch_vulnerability("VULN-0001")
    vuln = next(v for v in twin.dataset.vulnerabilities if v.id == "VULN-0001")
    assert vuln.patch_status == "patched"
    assert vuln.exploitability == 0.0

    # Delay patch for another vulnerability
    v2_before = twin.dataset.vulnerabilities[1].exploitability
    twin.delay_patch(twin.dataset.vulnerabilities[1].id, days=10)
    v2_after = twin.dataset.vulnerabilities[1].exploitability
    assert v2_after >= v2_before
