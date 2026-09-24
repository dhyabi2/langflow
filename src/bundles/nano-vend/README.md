# VendExtract (Nano x402) — Langflow Extension Bundle

Pay-per-call web extraction settled in **Nano (XNO)** via **x402** (`HTTP 402 Payment Required`).
No API key, no signup, no subscription — the Nano wallet is the account.

## What it does

`VendExtractComponent` calls a pay-per-call endpoint
(`https://extract.paypercall.dev/api/v1/extract?url=...`) that:

- answers `HTTP 402 Payment Required` with an x402 v2 challenge naming the
  price and destination (`accepts[]` → `nano:mainnet`, asset `XNO`), *or*
- serves the page after a free trial / payment.

The component then:
- returns the content on `HTTP 200`;
- on `HTTP 402`, returns the quoted price + `pay_to` so the user can pay in any
  Nano wallet and paste the settled block hash back into `payment_header`.

No wallet or seed is ever stored in the component.

## Why Nano / x402 for agent workflows

Agent commerce is moving to machine-native micropayments: an agent calls a
tool, the tool quotes a sub-cent price, the agent pays and gets the result.
Nano (XNO) settles in under a second at **zero fee** — so sub-cent per-call
prices have no floor. There is no gas, no L2, no merchant account, no card.

- x402 spec: https://x402.org
- Live manifest: https://extract.paypercall.dev/.well-known/x402

## Files

```
src/lfx_nano_vend/
├── __init__.py
├── extension.json          # bundle manifest
└── components/nano_vend/
    ├── __init__.py
    └── vend_extract.py     # the component
test_harness.py             # live unpaid-path test (no Langflow install needed)
```

## Test

```bash
python test_harness.py
```

Asserts the component's fetch shape answers the live endpoint (200 trial or
402 + price/pay_to), proving the integration is real, not fabricated.
