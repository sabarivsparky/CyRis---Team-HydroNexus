"""
REAL LOGIC — Named What-If Scenario Presets.

Pre-configured security intervention packages for executive boardroom decision sandboxing.
"""
from __future__ import annotations

from typing import Any

PRESETS: dict[str, dict[str, Any]] = {
    "mfa_everywhere": {
        "id": "mfa_everywhere",
        "label": "Enforce Phishing-Resistant MFA Everywhere",
        "description": "Deploys FIDO2 Phishing-Resistant MFA across all privileged identity principals.",
        "mutations": [{"type": "deploy_control", "control_id": "CTL-001"}],
    },
    "segment_subnet_b": {
        "id": "segment_subnet_b",
        "label": "Apply Micro-Segmentation to Subnet B",
        "description": "Enforces strict network micro-segmentation between app tier containers and core vault.",
        "mutations": [{"type": "deploy_control", "control_id": "CTL-002"}],
    },
    "zero_trust_microsegmentation": {
        "id": "zero_trust_microsegmentation",
        "label": "Zero-Trust IAM & Network Policy Engine",
        "description": "Deploys zero-trust identity policy engine blocking lateral credential reuse.",
        "mutations": [{"type": "deploy_control", "control_id": "CTL-010"}],
    },
    "patch_critical_vulns": {
        "id": "patch_critical_vulns",
        "label": "Remediate All Critical CVEs (CVSS >= 9.0)",
        "description": "Patches all open vulnerabilities with CVSS base score 9.0 or higher.",
        "mutations": [{"type": "patch_vulnerabilities", "min_cvss": 9.0}],
    },
    "patch_internet_facing": {
        "id": "patch_internet_facing",
        "label": "Patch Edge & Public-Facing Vulnerabilities",
        "description": "Patches all open vulnerabilities on DMZ and internet-facing assets.",
        "mutations": [
            {"type": "patch_vulnerabilities", "asset_id": "AST-001"},
            {"type": "patch_vulnerabilities", "asset_id": "AST-005"},
        ],
    },
    "delay_patch_30d": {
        "id": "delay_patch_30d",
        "label": "Delay Vulnerability Patching by 30 Days",
        "description": "Simulates 30-day patch delay across open vulnerabilities, increasing exploitability.",
        "mutations": [{"type": "delay_patch", "days": 30}],
    },
    "sever_service_account_pivot": {
        "id": "sever_service_account_pivot",
        "label": "Sever K8s Token Hijack Pivot Edge",
        "description": "Re-architects container network to sever service account token hijack pivot.",
        "mutations": [{"type": "remove_edge", "source": "AST-002", "target": "AST-004"}],
    },
}


def get_all_presets() -> list[dict[str, Any]]:
    """Return list of all available named what-if preset scenarios."""
    return list(PRESETS.values())


def get_preset(preset_id: str) -> dict[str, Any] | None:
    """Fetch preset scenario configuration by ID."""
    return PRESETS.get(preset_id)
