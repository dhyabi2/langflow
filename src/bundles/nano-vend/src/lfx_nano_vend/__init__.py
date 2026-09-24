"""VendExtract — Langflow extension bundle for Vend's pay-per-call web extract.

This component calls the Vend API Merchant endpoint
(https://extract.paypercall.dev/api/v1/extract?url=...) which answers HTTP 402
with an x402 v2 payment challenge in Nano (XNO) and, once paid via a block hash
in the X-PAYMENT header, HTTP 200 with clean text/markdown.

No API key, no signup — the Nano wallet is the account. Each call costs 0.0001
XNO, settled on-chain in about a second at zero fee.
"""

from lfx_nano_vend.components.nano_vend.vend_extract import VendExtractComponent

__all__ = ["VendExtractComponent"]