"""
REAL LOGIC — Production Smoke Test Script.

Hits every LIVE API endpoint, verifies HTTP 200 responses, validates JSON parsing,
and measures real operational network latencies.
"""
from __future__ import annotations

import sys
import time
import httpx


def run_smoke_test(base_url: str = "http://127.0.0.1:8000") -> bool:
    endpoints = [
        "/api/v1/health",
        "/api/v1/risk/summary",
        "/api/v1/risk/contributors?level=asset&limit=10",
        "/api/v1/risk/contributors?level=vulnerability&limit=10",
        "/api/v1/risk/contributors?level=business_unit&limit=10",
        "/api/v1/risk/trend",
    ]

    print(f"=== CYRIS SMOKE TEST: Target {base_url} ===")
    all_ok = True

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        for ep in endpoints:
            t0 = time.perf_counter()
            try:
                res = client.get(ep)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                if res.status_code == 200:
                    data = res.json()
                    status_str = f"200 OK (size: {len(res.content)} bytes)"
                else:
                    status_str = f"FAIL {res.status_code}"
                    all_ok = False
            except Exception as err:
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                status_str = f"ERROR: {err}"
                all_ok = False

            print(f"GET {ep:<50} [{status_str}] ({elapsed_ms:.2f} ms)")

    return all_ok


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    success = run_smoke_test(url)
    sys.exit(0 if success else 1)
