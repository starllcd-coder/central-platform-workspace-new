import json
import hashlib
import hmac
import time
from datetime import timedelta
from uuid import uuid4

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.billing.models import PaymentTransaction
from apps.pricing.models import CommissionRule
from apps.tenants.models import Module, Tenant, TenantModule

from .models import CentralPayment, GatewayConfig, GatewayProvider
from .models import PaymentRequestNonce
from .tasks import prune_payment_nonces_task


@override_settings(PAYMENT_GATEWAY_MODE="mock")
class PaymentFlowIntegrationTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            tenant_code="T-PAY-001",
            name="Pay Tenant",
            owner_email="pay@example.com",
            onboarding_fee_paid=True,
            pricing_model="one_time",
        )
        self.module = Module.objects.create(code="STAYLUX", name="StayLux")
        TenantModule.objects.create(
            tenant=self.tenant,
            module=self.module,
            enabled=True,
            marketplace_enabled=True,
        )
        CommissionRule.objects.create(
            tenant=self.tenant,
            module=self.module,
            booking_type="online",
            rate_percent="10.00",
            effective_from="2025-01-01",
            is_active=True,
        )

    def _signed_headers(self, method, path, body="", *, nonce=None, timestamp=None):
        timestamp = str(timestamp or int(time.time()))
        nonce = nonce or uuid4().hex
        signed = f"{timestamp}.{nonce}.{method.upper()}.{path}.".encode() + body.encode()
        signature = hmac.new(
            b"dev-payment-service-secret", signed, hashlib.sha256
        ).hexdigest()
        return {
            "HTTP_X_PAYMENT_TIMESTAMP": timestamp,
            "HTTP_X_PAYMENT_NONCE": nonce,
            "HTTP_X_PAYMENT_SIGNATURE": signature,
        }

    def _signed_post(self, url_name, payload, *, nonce=None):
        path = reverse(url_name)
        body = json.dumps(payload)
        return self.client.post(
            path,
            data=body,
            content_type="application/json",
            **self._signed_headers("POST", path, body, nonce=nonce),
        )

    def test_create_and_verify_payment_posts_transaction(self):
        create_payload = {
            "tenant_id": self.tenant.id,
            "module_code": self.module.code,
            "amount": "100.00",
            "currency": "OMR",
            "booking_id": "BK-1001",
            "idempotency_key": "idem-1001",
        }
        create_res = self._signed_post("paymentsvc-create-payment", create_payload)
        self.assertIn(create_res.status_code, [200, 201])
        payment_id = create_res.json()["payment"]["payment_id"]

        verify_res = self._signed_post(
            "paymentsvc-verify-payment", {"payment_id": payment_id}
        )
        self.assertEqual(verify_res.status_code, 200)
        self.assertEqual(verify_res.json()["payment"]["transaction_status"], "captured")
        self.assertTrue(PaymentTransaction.objects.filter(tenant=self.tenant, booking_ref="BK-1001").exists())

    def test_demo_tenant_payment_creation_is_blocked(self):
        self.tenant.account_type = "demo"
        self.tenant.demo_expires_on = timezone.localdate() + timedelta(days=14)
        self.tenant.save(update_fields=["account_type", "demo_expires_on", "updated_at"])
        create_payload = {
            "tenant_id": self.tenant.id,
            "module_code": self.module.code,
            "amount": "100.00",
            "currency": "OMR",
            "booking_id": "BK-DEMO-1001",
            "idempotency_key": "idem-demo-1001",
        }
        response = self._signed_post("paymentsvc-create-payment", create_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("demo sandbox", response.json()["detail"].lower())

    def test_unsigned_payment_request_is_rejected(self):
        response = self.client.post(
            reverse("paymentsvc-create-payment"),
            data=json.dumps({"tenant_id": self.tenant.id, "amount": "10.00"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_payment_request_nonce_cannot_be_replayed(self):
        payload = {
            "tenant_id": self.tenant.id,
            "amount": "10.00",
            "idempotency_key": "replay-payment",
        }
        nonce = uuid4().hex
        first = self._signed_post("paymentsvc-create-payment", payload, nonce=nonce)
        second = self._signed_post("paymentsvc-create-payment", payload, nonce=nonce)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 403)
        self.assertIn("replay", second.json()["detail"].lower())

    def test_repeated_verification_does_not_duplicate_billing_transaction(self):
        create = self._signed_post(
            "paymentsvc-create-payment",
            {
                "tenant_id": self.tenant.id,
                "module_code": self.module.code,
                "amount": "35.00",
                "booking_id": "BK-IDEMPOTENT",
            },
        )
        payment_id = create.json()["payment"]["payment_id"]

        first = self._signed_post("paymentsvc-verify-payment", {"payment_id": payment_id})
        second = self._signed_post("paymentsvc-verify-payment", {"payment_id": payment_id})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            PaymentTransaction.objects.filter(booking_ref="BK-IDEMPOTENT").count(), 1
        )

    def test_invalid_payment_and_refund_amounts_are_rejected(self):
        create = self._signed_post(
            "paymentsvc-create-payment",
            {"tenant_id": self.tenant.id, "amount": "-1.00"},
        )
        self.assertEqual(create.status_code, 400)

        valid = self._signed_post(
            "paymentsvc-create-payment",
            {"tenant_id": self.tenant.id, "amount": "20.00"},
        )
        payment_id = valid.json()["payment"]["payment_id"]
        self._signed_post("paymentsvc-verify-payment", {"payment_id": payment_id})
        refund = self._signed_post(
            "paymentsvc-refund-payment",
            {"payment_id": payment_id, "amount": "21.00"},
        )
        self.assertEqual(refund.status_code, 400)
        self.assertIn("exceeds", refund.json()["detail"].lower())

    def test_webhook_without_configured_secret_fails_closed(self):
        response = self.client.post(
            reverse("paymentsvc-webhook-stripe"),
            data=json.dumps({"event_id": "evt-no-secret", "status": "paid"}),
            content_type="application/json",
            HTTP_X_GATEWAY_TIMESTAMP=str(int(time.time())),
            HTTP_X_GATEWAY_SIGNATURE="forged",
        )
        self.assertEqual(response.status_code, 403)

    def test_valid_duplicate_webhook_is_processed_once(self):
        config = GatewayConfig(provider=GatewayProvider.STRIPE, is_enabled=True)
        config.set_webhook_secret("gateway-webhook-test-secret")
        config.save()
        payment = CentralPayment.objects.create(
            payment_id="pay_webhook_test",
            tenant=self.tenant,
            module=self.module,
            gateway_name=GatewayProvider.STRIPE,
            amount="25.00",
            commission_amount="2.50",
            business_share="22.50",
            transaction_status="pending",
            external_reference="stripe_webhook_ref",
        )
        payload = {
            "event_id": "evt-once",
            "status": "paid",
            "payment_ref": payment.external_reference,
        }
        body = json.dumps(payload)
        timestamp = str(int(time.time()))
        signature = hmac.new(
            b"gateway-webhook-test-secret",
            f"{timestamp}.".encode() + body.encode(),
            hashlib.sha256,
        ).hexdigest()

        for _ in range(2):
            response = self.client.post(
                reverse("paymentsvc-webhook-stripe"),
                data=body,
                content_type="application/json",
                HTTP_X_GATEWAY_TIMESTAMP=timestamp,
                HTTP_X_GATEWAY_SIGNATURE=signature,
            )
            self.assertEqual(response.status_code, 200)
        self.assertEqual(
            PaymentTransaction.objects.filter(booking_ref=payment.payment_id).count(), 1
        )

    @override_settings(PAYMENT_GATEWAY_MODE="disabled")
    def test_mock_gateway_cannot_run_when_payment_mode_is_disabled(self):
        response = self._signed_post(
            "paymentsvc-create-payment",
            {"tenant_id": self.tenant.id, "amount": "10.00"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("disabled", response.json()["detail"].lower())

    def test_gateway_secrets_are_encrypted_at_rest(self):
        config = GatewayConfig(provider=GatewayProvider.TAP)
        config.set_secret_key("gateway-api-secret")
        config.set_webhook_secret("gateway-webhook-secret")
        config.save()
        config.refresh_from_db()

        self.assertNotIn("gateway-api-secret", config.secret_key_encrypted)
        self.assertNotIn("gateway-webhook-secret", config.webhook_secret_encrypted)
        self.assertEqual(config.get_secret_key(), "gateway-api-secret")
        self.assertEqual(config.get_webhook_secret(), "gateway-webhook-secret")

    def test_old_payment_nonces_are_pruned(self):
        old = PaymentRequestNonce.objects.create(
            nonce="old-payment-nonce",
            method="POST",
            path="/payments/api/create-payment/",
            source_timestamp=timezone.now() - timedelta(days=8),
            request_signature="a" * 64,
        )
        PaymentRequestNonce.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=8)
        )
        PaymentRequestNonce.objects.create(
            nonce="new-payment-nonce",
            method="POST",
            path="/payments/api/create-payment/",
            source_timestamp=timezone.now(),
            request_signature="b" * 64,
        )

        result = prune_payment_nonces_task()

        self.assertEqual(result["deleted"], 1)
        self.assertEqual(
            set(PaymentRequestNonce.objects.values_list("nonce", flat=True)),
            {"new-payment-nonce"},
        )
