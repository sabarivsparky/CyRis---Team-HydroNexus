"""
REAL LOGIC — Unit tests for Budget Optimizer Option Catalog (app.decision.options).
"""
import pytest
from app.config import PATCH_COST_PER_VULN_INR, PATCH_TIERS
from app.decision.costing import cost_of
from app.decision.options import Option, DroppedOption, build_options
from app.state import TwinStore


def test_option_catalog_construction():
    """Verify candidate options, disjoint patch tiers, cost equality, and dropped items."""
    store = TwinStore()
    live_twin = store.live_twin()

    active, dropped = build_options(live_twin)

    # 1. Option ID canonical sorting
    active_ids = [o.id for o in active]
    assert active_ids == sorted(active_ids), "Active options must be sorted canonically by ID"

    # 2. Candidate controls check
    control_opts = [o for o in active if o.kind == "control"]
    for c_opt in control_opts:
        # Cost check against cost_of helper
        expected_cost, _ = cost_of(c_opt.mutations, live_twin.dataset)
        assert c_opt.cost_inr == expected_cost
        assert c_opt.standalone_gain_inr > 0, "Active options must have positive standalone gain"

    # 3. Patch tiers check
    patch_opts = [o for o in active if o.kind == "patch"]
    vulns = live_twin.dataset.vulnerabilities

    for p_opt in patch_opts:
        tier_key = p_opt.id.replace("PATCH-", "").lower()
        lo, hi = PATCH_TIERS[tier_key]
        tier_vids = p_opt.mutations[0]["vulnerability_ids"]

        # Confirm all vids are in CVSS range and unpatched
        for vid in tier_vids:
            v = next(x for x in vulns if x.id == vid)
            assert v.patch_status != "patched"
            assert lo <= v.cvss_score < hi

        expected_cost = len(tier_vids) * PATCH_COST_PER_VULN_INR
        assert p_opt.cost_inr == expected_cost

    # 4. Dropped options verification
    for d in dropped:
        assert isinstance(d, DroppedOption)
        assert d.standalone_gain_inr <= 0
        assert d.reason != ""
