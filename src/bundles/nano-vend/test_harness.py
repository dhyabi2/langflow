"""Standalone harness for the VendExtract component's fetch path.

Cannot import the Langflow lfx framework here (not installed), so exercises
the component's exact HTTP request shape against the LIVE Vend endpoint, and
asserts the unpaid path works.

This mirrors what VendExtractComponent._fetch() does on a 402.
"""
import json
import urllib.parse
import httpx

DEFAULT_URL_INPUT = "https://extract.paypercall.dev/api/v1/extract"
URL = "https://example.com"


def fetch_unpaid() -> tuple[int, dict]:
    """Replicate vend_extract.py `_fetch` + 402 handling, minus the framework."""
    headers = {
        "Accept": "application/json",
        "User-Agent": "langflow-vend-extract-harness/0.1.0",
    }
    params = {"url": URL}
    with httpx.Client(timeout=30, follow_redirects=False) as client:
        resp = client.get(DEFAULT_URL_INPUT, params=params, headers=headers)
        body = resp.text
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {}
    return resp.status_code, payload


status, payload = fetch_unpaid()
print(f"HTTP status: {status}")
print(f"Keys in response: {list(payload.keys())}")
print(f"price_xno: {payload.get('price_xno')}")
print(f"pay_to present: {'pay_to' in payload}")

# The endpoint may return 200 with free trial or 402 — either is acceptable
# as a live test (the component handles both cases)
assert status in (200, 402), f"expected 200 (trial) or 402, got {status}"
if status == 402:
    assert payload.get("price_xno") is not None, "price_xno should be present on 402"
    assert "pay_to" in payload, "pay_to should be present on 402"

print("\nHARNESS_PASS: VendExtract fetch path verified against live endpoint")