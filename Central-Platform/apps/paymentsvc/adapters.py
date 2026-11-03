from __future__ import annotations

from decimal import Decimal
from uuid import uuid4


class BaseGatewayAdapter:
    provider = "base"

    def create_payment_session(self, *, payment_id: str, amount: Decimal, currency: str, metadata: dict) -> dict:
        token = uuid4().hex
        return {
            "gateway_payment_ref": f"{self.provider}_{token}",
            "checkout_url": f"https://mock.{self.provider}.pay/checkout/{token}",
            "status": "pending",
        }

    def verify_payment(self, *, external_reference: str) -> dict:
        return {"status": "captured", "external_reference": external_reference}

    def refund_payment(self, *, external_reference: str, amount: Decimal, reason: str) -> dict:
        return {
            "refund_reference": f"rf_{self.provider}_{uuid4().hex[:16]}",
            "status": "processed",
            "amount": str(amount),
            "reason": reason,
        }


class ThawaniAdapter(BaseGatewayAdapter):
    provider = "thawani"


class TapAdapter(BaseGatewayAdapter):
    provider = "tap"


class StripeAdapter(BaseGatewayAdapter):
    provider = "stripe"

