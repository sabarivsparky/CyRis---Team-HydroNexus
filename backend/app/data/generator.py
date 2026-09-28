"""
REAL LOGIC — Synthetic data generator for CyRIS.

Generates deterministic enterprise assets, vulnerabilities, security controls,
and exploit edges seeded by default with DEFAULT_SEED (42).
"""
from __future__ import annotations

import datetime
import json
import math
import random
from pathlib import Path

from app.config import AS_OF_DATE_ISO, DEFAULT_SEED
from app.schemas import Asset, Control, Dataset, ExploitEdge, Vulnerability

# Default dataset path
DATASET_PATH = Path(__file__).parent.parent.parent / "data" / "generated" / "dataset.json"


# Hardcoded core 5 assets from blueprint / decision log D-012
HARDCODED_ASSETS = [
    Asset(
        id="AST-001",
        name="Mobile Banking API Front-End",
        asset_type="api_gateway",
        business_unit="Digital Channels",
        criticality=3,
        annual_revenue_dependency_inr=500_000_000,
        data_sensitivity=4,
        internet_facing=True,
        is_crown_jewel=False,
        subnet="Subnet A",
    ),
    Asset(
        id="AST-002",
        name="Authentication Microservice Container",
        asset_type="microservice",
        business_unit="Digital Channels",
        criticality=4,
        annual_revenue_dependency_inr=1_200_000_000,
        data_sensitivity=4,
        internet_facing=False,
        is_crown_jewel=False,
        subnet="Subnet B",
    ),
    Asset(
        id="AST-003",
        name="Core Transaction Database Vault",
        asset_type="database",
        business_unit="Core Banking",
        criticality=5,
        annual_revenue_dependency_inr=5_000_000_000,
        data_sensitivity=5,
        internet_facing=False,
        is_crown_jewel=True,
        subnet="Subnet C",
    ),
    Asset(
        id="AST-004",
        name="Privileged Active Directory Service Principal Account",
        asset_type="identity",
        business_unit="Shared IT",
        criticality=5,
        annual_revenue_dependency_inr=3_000_000_000,
        data_sensitivity=5,
        internet_facing=False,
        is_crown_jewel=True,
        subnet="Subnet B",
    ),
    Asset(
        id="AST-005",
        name="Payment Gateway Edge Proxy",
        asset_type="web_frontend",
        business_unit="Payments",
        criticality=4,
        annual_revenue_dependency_inr=2_500_000_000,
        data_sensitivity=4,
        internet_facing=True,
        is_crown_jewel=False,
        subnet="Subnet A",
    ),
]

# Additional asset names pool (20 items for AST-006 to AST-025)
SYNTHETIC_ASSET_NAMES = [
    ("Treasury Settlement Engine", "microservice", "Treasury"),
    ("SWIFT Integration Gateway", "api_gateway", "Treasury"),
    ("Customer Onboarding Portal", "web_frontend", "Digital Channels"),
    ("Core Banking Mainframe Adapter", "application_server", "Core Banking"),
    ("Corporate Payments Portal", "web_frontend", "Payments"),
    ("ATM Controller Cluster", "microservice", "Digital Channels"),
    ("Retail Loan Origination Service", "application_server", "Core Banking"),
    ("Credit Card Fraud Detection Engine", "microservice", "Payments"),
    ("Customer Identity Directory (LDAP)", "identity", "Shared IT"),
    ("Centralized Log Collector (Splunk)", "cloud_workload", "Shared IT"),
    ("DMZ Perimeter Firewall Cluster", "network_device", "Shared IT"),
    ("Core Internal Router Pair", "network_device", "Shared IT"),
    ("General Ledger Database", "database", "Core Banking"),
    ("Customer PII Data Lake", "database", "Digital Channels"),
    ("Wealth Management Portal", "web_frontend", "Digital Channels"),
    ("Third-Party Payment Partner Switch", "third_party", "Payments"),
    ("Enterprise Analytics Engine", "cloud_workload", "Shared IT"),
    ("Internal Employee Portal", "web_frontend", "Shared IT"),
    ("Regulatory Reporting Database", "database", "Treasury"),
    ("Mobile Notification Gateway", "microservice", "Digital Channels"),
]

# Revenue ranges by criticality (low, high in INR) — log-uniform bounds (D-011)
CRITICALITY_REVENUE_BOUNDS = {
    1: (100_000, 5_000_000),             # ₹1L – ₹50L
    2: (5_000_000, 50_000_000),          # ₹50L – ₹5Cr
    3: (50_000_000, 500_000_000),        # ₹5Cr – ₹50Cr
    4: (500_000_000, 3_000_000_000),     # ₹50Cr – ₹300Cr
    5: (3_000_000_000, 20_000_000_000),  # ₹300Cr – ₹2000Cr
}


def _draw_log_uniform(rng: random.Random, low: float, high: float) -> int:
    """Draw integer INR from log-uniform distribution [low, high]."""
    val = math.exp(rng.uniform(math.log(low), math.log(high)))
    return int(val)


def generate_dataset(seed: int = DEFAULT_SEED) -> Dataset:
    """Generate deterministic synthetic enterprise dataset."""
    rng = random.Random(seed)

    # 1. Assets
    assets: list[Asset] = list(HARDCODED_ASSETS)

    # Generate AST-006 to AST-025
    for i, (name, asset_type, bu) in enumerate(SYNTHETIC_ASSET_NAMES, start=6):
        asset_id = f"AST-{i:03d}"
        # Determine criticality and subnet distribution
        if i in (6, 7, 8, 12, 13, 14, 18, 19):
            criticality = rng.choice([4, 5])
        elif i in (9, 10, 11, 15, 16, 17):
            criticality = rng.choice([3, 4])
        else:
            criticality = rng.choice([1, 2, 3])

        is_crown_jewel = (criticality == 5)
        internet_facing = (asset_type in ("web_frontend", "api_gateway", "third_party")) and (rng.random() < 0.6)

        if internet_facing:
            subnet = "Subnet A"
        elif criticality >= 4 and asset_type in ("database", "identity"):
            subnet = rng.choice(["Subnet B", "Subnet C"])
        else:
            subnet = rng.choice(["Subnet A", "Subnet B", "Subnet C"])

        low_rev, high_rev = CRITICALITY_REVENUE_BOUNDS[criticality]
        revenue_dep = _draw_log_uniform(rng, low_rev, high_rev)
        data_sensitivity = criticality if is_crown_jewel else rng.randint(max(1, criticality - 1), min(5, criticality + 1))

        assets.append(
            Asset(
                id=asset_id,
                name=name,
                asset_type=asset_type,
                business_unit=bu,
                criticality=criticality,
                annual_revenue_dependency_inr=revenue_dep,
                data_sensitivity=data_sensitivity,
                internet_facing=internet_facing,
                is_crown_jewel=is_crown_jewel,
                subnet=subnet,
            )
        )

    # 2. Vulnerabilities
    vulnerabilities: list[Vulnerability] = [
        # Hardcoded key vulnerabilities
        Vulnerability(
            id="VULN-0001",
            cve_id="CVE-2026-3827",
            asset_id="AST-001",
            title="Remote Code Execution in API Gateway Edge",
            category="access_control",
            cvss_score=9.8,
            exploitability=0.90,
            patch_status="unpatched",
            discovered_date=datetime.date(2026, 7, 15),
        ),
        Vulnerability(
            id="VULN-0002",
            cve_id="CVE-2026-1002",
            asset_id="AST-002",
            title="Environment Variable Leakage & Container Privilege Escalation",
            category="misconfiguration",
            cvss_score=8.5,
            exploitability=0.75,
            patch_status="unpatched",
            discovered_date=datetime.date(2026, 8, 1),
        ),
        Vulnerability(
            id="VULN-0003",
            cve_id="CVE-2026-1003",
            asset_id="AST-004",
            title="Active Directory Kerberoasting & Token Impersonation",
            category="access_control",
            cvss_score=8.8,
            exploitability=0.80,
            patch_status="unpatched",
            discovered_date=datetime.date(2026, 8, 10),
        ),
        Vulnerability(
            id="VULN-0004",
            cve_id="CVE-2026-1004",
            asset_id="AST-005",
            title="Payment Edge Proxy Request Smuggling",
            category="network_security",
            cvss_score=8.1,
            exploitability=0.70,
            patch_status="patch_available",
            discovered_date=datetime.date(2026, 8, 20),
        ),
    ]

    vuln_counter = 5
    categories = [
        "access_control", "patch_management", "network_security",
        "misconfiguration", "data_protection", "logging_monitoring",
    ]
    patch_statuses = ["unpatched", "patch_available", "patched"]
    patch_weights = [0.4, 0.4, 0.2]

    base_date = datetime.date(2026, 1, 1)

    for asset in assets:
        # Guarantee 1-3 vulnerabilities per asset (excluding the hardcoded ones if already enough)
        existing_count = sum(1 for v in vulnerabilities if v.asset_id == asset.id)
        num_vulns = rng.randint(1, 2) if existing_count > 0 else rng.randint(1, 3)

        for _ in range(num_vulns):
            vuln_id = f"VULN-{vuln_counter:04d}"
            vuln_counter += 1
            cve_id = f"CVE-2026-{rng.randint(2000, 9999)}"
            category = rng.choice(categories)
            cvss = round(rng.uniform(4.0, 9.5), 1)
            exploitability = round(min(0.99, max(0.1, (cvss / 10.0) * rng.uniform(0.7, 1.1))), 2)
            patch_status = rng.choices(patch_statuses, weights=patch_weights)[0]
            days_offset = rng.randint(0, 250)
            disc_date = base_date + datetime.timedelta(days=days_offset)

            vulnerabilities.append(
                Vulnerability(
                    id=vuln_id,
                    cve_id=cve_id,
                    asset_id=asset.id,
                    title=f"{category.replace('_', ' ').title()} flaw on {asset.name}",
                    category=category,
                    cvss_score=cvss,
                    exploitability=exploitability,
                    patch_status=patch_status,
                    discovered_date=disc_date,
                )
            )

    # 3. Security Controls (Candidate and Deployed)
    controls: list[Control] = [
        Control(
            id="CTL-001",
            name="Phishing-Resistant MFA Enforcement",
            category="access_control",
            cost_inr=1_800_000,
            effectiveness=0.85,
            impact_reduction=0.0,
            dampens_edge_types={"credential_reuse": 0.85, "token_hijack": 0.70},
            covered_asset_ids=["AST-002", "AST-004"],
            status="candidate",
            health=1.0,
        ),
        Control(
            id="CTL-002",
            name="Strict Subnet Micro-Segmentation",
            category="network_security",
            cost_inr=2_500_000,
            effectiveness=0.80,
            impact_reduction=0.20,
            dampens_edge_types={"network_access": 0.80, "service_call": 0.75},
            covered_asset_ids=["AST-001", "AST-002", "AST-003", "AST-005"],
            status="candidate",
            health=1.0,
        ),
        Control(
            id="CTL-003",
            name="API Gateway Web Application Firewall (WAF)",
            category="network_security",
            cost_inr=800_000,
            effectiveness=0.75,
            impact_reduction=0.10,
            dampens_edge_types={"network_access": 0.75},
            covered_asset_ids=["AST-001", "AST-005"],
            status="candidate",
            health=1.0,
        ),
        Control(
            id="CTL-004",
            name="EDR Host Agent Coverage Expansion",
            category="logging_monitoring",
            cost_inr=1_200_000,
            effectiveness=0.70,
            impact_reduction=0.30,
            dampens_edge_types={"token_hijack": 0.65, "trust_relationship": 0.60},
            covered_asset_ids=["AST-002", "AST-004", "AST-006", "AST-007"],
            status="candidate",
            health=1.0,
        ),
        Control(
            id="CTL-005",
            name="Automated Vulnerability Patching Pipeline",
            category="patch_management",
            cost_inr=1_500_000,
            effectiveness=0.90,
            impact_reduction=0.0,
            dampens_edge_types={"network_access": 0.50, "service_call": 0.50},
            covered_asset_ids=[a.id for a in assets if a.criticality >= 3],
            status="candidate",
            health=1.0,
        ),
        Control(
            id="CTL-006",
            name="Database Vault & HSM Field-Level Encryption",
            category="data_protection",
            cost_inr=3_500_000,
            effectiveness=0.60,
            impact_reduction=0.85,
            dampens_edge_types={"data_flow": 0.90, "trust_relationship": 0.70},
            covered_asset_ids=["AST-003", "AST-018", "AST-024"],
            status="candidate",
            health=1.0,
        ),
        Control(
            id="CTL-007",
            name="Privileged Access Management (PAM) Vaulting",
            category="access_control",
            cost_inr=2_200_000,
            effectiveness=0.88,
            impact_reduction=0.15,
            dampens_edge_types={"credential_reuse": 0.90, "token_hijack": 0.85},
            covered_asset_ids=["AST-004", "AST-014"],
            status="deployed",
            health=0.85,
        ),
        Control(
            id="CTL-008",
            name="Perimeter DDoS & Traffic Scrubbing",
            category="network_security",
            cost_inr=1_000_000,
            effectiveness=0.80,
            impact_reduction=0.50,
            dampens_edge_types={"network_access": 0.80},
            covered_asset_ids=["AST-001", "AST-005"],
            status="deployed",
            health=0.95,
        ),
        Control(
            id="CTL-009",
            name="SIEM Real-Time SOAR Incident Response",
            category="logging_monitoring",
            cost_inr=2_000_000,
            effectiveness=0.65,
            impact_reduction=0.40,
            dampens_edge_types={"credential_reuse": 0.50, "token_hijack": 0.50},
            covered_asset_ids=[a.id for a in assets],
            status="deployed",
            health=0.90,
        ),
        Control(
            id="CTL-010",
            name="Zero-Trust IAM Policy Engine",
            category="access_control",
            cost_inr=3_000_000,
            effectiveness=0.82,
            impact_reduction=0.25,
            dampens_edge_types={"credential_reuse": 0.80, "trust_relationship": 0.80},
            covered_asset_ids=["AST-002", "AST-004"],
            status="candidate",
            health=1.0,
        ),
    ]

    # 4. Exploit Edges (Attack Graph topology)
    edges: list[ExploitEdge] = [
        # Ingress edges from INTERNET
        ExploitEdge(
            source="INTERNET",
            target="AST-001",
            relationship_type="network_access",
            exploit_probability=0.90,
            description="Public HTTPS ingress to Mobile Banking API Gateway (CVE-2026-3827)",
        ),
        ExploitEdge(
            source="INTERNET",
            target="AST-005",
            relationship_type="network_access",
            exploit_probability=0.85,
            description="Public ingress to Payment Gateway Edge Proxy (CVE-2026-1004)",
        ),
        # Primary attack path from blueprint
        ExploitEdge(
            source="AST-001",
            target="AST-002",
            relationship_type="service_call",
            exploit_probability=0.75,
            description="Pivots via leaked environment variables from API edge to Auth Container",
        ),
        ExploitEdge(
            source="AST-002",
            target="AST-004",
            relationship_type="token_hijack",
            exploit_probability=0.80,
            description="Hijacks active Kubernetes Service Account Token to reach AD Principal Account",
        ),
        ExploitEdge(
            source="AST-004",
            target="AST-003",
            relationship_type="credential_reuse",
            exploit_probability=0.88,
            description="Lateral network traversal to Core Transaction DB Vault via AD Service Principal",
        ),
        # Alternative paths
        ExploitEdge(
            source="AST-005",
            target="AST-002",
            relationship_type="service_call",
            exploit_probability=0.70,
            description="Internal REST call from Payment Edge to Auth Microservice",
        ),
        ExploitEdge(
            source="AST-002",
            target="AST-003",
            relationship_type="data_flow",
            exploit_probability=0.60,
            description="Direct SQL connection pool access from Auth Container to DB Vault",
        ),
    ]

    # Add further connectivity edges for remaining synthetic assets
    edge_counter = len(edges) + 1
    subnet_a = [a for a in assets if a.subnet == "Subnet A" and a.id not in ("AST-001", "AST-005")]
    subnet_b = [a for a in assets if a.subnet == "Subnet B" and a.id not in ("AST-002", "AST-004")]
    subnet_c = [a for a in assets if a.subnet == "Subnet C" and a.id != "AST-003"]

    # Ingress to other Subnet A assets
    for a in subnet_a:
        if a.internet_facing:
            edges.append(
                ExploitEdge(
                    source="INTERNET",
                    target=a.id,
                    relationship_type="network_access",
                    exploit_probability=round(rng.uniform(0.50, 0.80), 2),
                    description=f"Public access to {a.name}",
                )
            )

    # Subnet A -> Subnet B links
    for a_src in [a for a in assets if a.subnet == "Subnet A"][:4]:
        for a_tgt in [a for a in assets if a.subnet == "Subnet B"][:4]:
            if a_src.id != a_tgt.id and rng.random() < 0.4:
                edges.append(
                    ExploitEdge(
                        source=a_src.id,
                        target=a_tgt.id,
                        relationship_type=rng.choice(["service_call", "trust_relationship"]),
                        exploit_probability=round(rng.uniform(0.40, 0.75), 2),
                        description=f"Internal pivot from {a_src.id} to {a_tgt.id}",
                    )
                )

    # Subnet B -> Subnet C links (targeting database/crown jewels)
    for b_src in [a for a in assets if a.subnet == "Subnet B"][:4]:
        for c_tgt in [a for a in assets if a.subnet == "Subnet C"][:3]:
            if b_src.id != c_tgt.id and rng.random() < 0.5:
                edges.append(
                    ExploitEdge(
                        source=b_src.id,
                        target=c_tgt.id,
                        relationship_type=rng.choice(["credential_reuse", "data_flow"]),
                        exploit_probability=round(rng.uniform(0.50, 0.85), 2),
                        description=f"Lateral pivot from {b_src.id} to core target {c_tgt.id}",
                    )
                )

    as_of = datetime.date.fromisoformat(AS_OF_DATE_ISO)
    return Dataset(
        assets=assets,
        vulnerabilities=vulnerabilities,
        controls=controls,
        edges=edges,
        as_of=as_of,
    )


def save_dataset(dataset: Dataset, path: str | Path | None = None) -> Path:
    """Save dataset to JSON file."""
    target_path = Path(path) if path else DATASET_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(dataset.model_dump_json(indent=2))
    return target_path


def load_dataset(path: str | Path | None = None) -> Dataset:
    """Load dataset from JSON file."""
    target_path = Path(path) if path else DATASET_PATH
    if not target_path.exists():
        dataset = generate_dataset()
        save_dataset(dataset, target_path)
        return dataset
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Dataset.model_validate(data)
