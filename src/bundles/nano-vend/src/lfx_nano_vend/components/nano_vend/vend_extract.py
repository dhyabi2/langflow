"""VendExtract component — calls Vend's pay-per-call web extraction, settled in Nano (XNO).

Payment models:
  - Per-call x402: put a settled 64-char Nano block hash in `payment_header`
    (sent as X-PAYMENT header).
  - Prepaid balance: put a nano_... account with a prepaid balance on the
    Vend server in `balance_account` (sent as X-BALANCE header); calls deduct.
  - No wallet or seed is stored in the component — the user manages their own
    Nano wallet.
"""

from __future__ import annotations

import json

import httpx

from lfx.custom.custom_component.component import Component
from lfx.inputs.inputs import MessageTextInput
from lfx.schema.message import Message
from lfx.template.field.base import Output

DEFAULT_TIMEOUT = 30
DEFAULT_URL_INPUT = "https://extract.paypercall.dev/api/v1/extract"


class VendExtractComponent(Component):
    """Extract clean text/markdown from a web page, paid per call in Nano (XNO)."""

    display_name = "Vend Extract (Nano x402)"
    description = (
        "Pay-per-call web extraction settled in Nano (XNO) via x402. "
        "No API key, no signup — each call to a Vend endpoint costs 0.0001 XNO "
        "or uses a free trial."
    )
    documentation: str = "https://extract.paypercall.dev/"
    icon = "webhook"
    name = "VendExtract"

    inputs = [
        MessageTextInput(
            name="url",
            display_name="URL",
            info="Full URL of the page to extract clean text from.",
            placeholder="https://example.com",
            required=True,
        ),
        MessageTextInput(
            name="endpoint",
            display_name="Endpoint",
            info="Vend (or compatible) extract endpoint.",
            advanced=True,
            value=DEFAULT_URL_INPUT,
        ),
        MessageTextInput(
            name="payment_header",
            display_name="Payment header (settled Nano block hash)",
            info=(
                "A settled 64-char Nano block hash (X-PAYMENT header). "
                "Leave empty — the component returns the payment challenge."
            ),
            advanced=True,
            value="",
        ),
        MessageTextInput(
            name="balance_account",
            display_name="Prepaid balance account",
            info=(
                "A nano_... account holding a prepaid balance on the Vend "
                "server; calls deduct from it (X-BALANCE header)."
            ),
            advanced=True,
            value="",
        ),
    ]

    outputs = [
        Output(display_name="Content", name="content", method="fetch_content"),
    ]

    async def _fetch(self) -> tuple[int, str]:
        """Call the endpoint. Returns (status_code, body_text)."""
        url = (self.endpoint or DEFAULT_URL_INPUT).rstrip("/")
        params = {"url": self.url}
        headers = {
            "Accept": "application/json",
            "User-Agent": "langflow-vend-extract/0.1.0",
        }
        if self.payment_header:
            headers["X-PAYMENT"] = self.payment_header.strip()
        if self.balance_account:
            headers["X-BALANCE"] = self.balance_account.strip()
        async with httpx.AsyncClient(
            timeout=DEFAULT_TIMEOUT, follow_redirects=False
        ) as client:
            resp = await client.get(url, params=params, headers=headers)
            return resp.status_code, resp.text

    async def fetch_content(self) -> Message:
        """Fetch paid content, or explain the payment required."""
        status, body = await self._fetch()

        if status == 200:
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {}
            text = " ".join(
                str(payload.get(k, ""))
                for k in ("title", "text", "markdown", "error")
                if payload.get(k)
            ).strip()
            text = text or body
            self.status = "Content retrieved successfully."
            return Message(text=text[:100_000], properties={"data": payload})

        if status == 402:
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {}
            price = payload.get("price_xno")
            pay_to = payload.get("pay_to")
            msg = (
                "This call requires payment in Nano (XNO), settled on-chain "
                "in about a second at zero fee. "
                + (
                    f"Pay {price} XNO to {pay_to} in any Nano wallet, then "
                    f"paste the resulting block hash into this component's "
                    f"'payment_header' input and re-run."
                    if price and pay_to
                    else "Configure payment_header (a settled Nano block hash) "
                    "or balance_account (a nano_... prepaid balance)."
                )
            )
            self.status = "Payment required before content is returned."
            return Message(text=msg, properties={"data": payload})

        self.status = f"Endpoint answered HTTP {status}."
        return Message(
            text=f"Endpoint answered HTTP {status}:\n{body[:2000]}",
            properties={"data": {"status": status, "body": body[:2000]}},
        )