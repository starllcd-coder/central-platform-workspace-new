import hashlib
import hmac
import json
import time
import uuid
from datetime import timedelta
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from apps.marketplace.models import MarketplaceBooking
from apps.tenants.models import Module, Tenant
from .models import ConnectorEvent

@override_settings(CONNECTOR_SHARED_SECRET="test-status-secret", CONNECTOR_REQUIRE_SIGNED_REQUESTS=True)
class LifecycleTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(tenant_code="T-ONE", name="One")
        self.other = Tenant.objects.create(tenant_code="T-TWO", name="Two")
        self.module = Module.objects.create(code="drivesphere", name="DriveSphere")
        self.booking = MarketplaceBooking.objects.create(booking_id="NXV-ONE", tenant=self.tenant, module=self.module)

    def post(self, status="confirmed", timestamp=None, tenant="T-ONE", event_id=None):
        payload = {"tenant_code": tenant, "module_code": "drivesphere", "event_name": "marketplace.booking.updated",
            "external_event_id": event_id or uuid.uuid4().hex, "data": {"booking_id": "NXV-ONE", "status": status,
            "updated_at": timestamp or timezone.now().isoformat()}}
        raw = json.dumps(payload).encode()
        ts = str(int(time.time()))
        nonce = uuid.uuid4().hex
        sig = hmac.new(b"test-status-secret", f"{ts}.{nonce}.".encode() + raw, hashlib.sha256).hexdigest()
        return self.client.post(reverse("connector-webhooks-events"), raw, content_type="application/json",
            HTTP_X_CONNECTOR_SECRET="test-status-secret", HTTP_X_CONNECTOR_TIMESTAMP=ts,
            HTTP_X_CONNECTOR_NONCE=nonce, HTTP_X_CONNECTOR_SIGNATURE=sig)

    def test_signed_provider_completion_is_visible_in_marketplace(self):
        response = self.post("completed")
        self.assertEqual(response.status_code, 200, response.content)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "completed")
        self.assertEqual(self.booking.fulfillment_status, "provider_confirmed")
        self.assertEqual(self.booking.payment_status, "unpaid")

    def test_cross_tenant_event_cannot_change_booking(self):
        self.assertEqual(self.post("cancelled", tenant="T-TWO").status_code, 422)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "pending")
        self.assertEqual(ConnectorEvent.objects.count(), 0)

    def test_older_event_cannot_undo_newer_status(self):
        now = timezone.now()
        self.assertEqual(self.post("confirmed", timestamp=now.isoformat()).status_code, 200)
        self.assertEqual(self.post("pending", timestamp=(now-timedelta(minutes=1)).isoformat()).status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "confirmed")

    def test_terminal_booking_cannot_be_resurrected(self):
        self.assertEqual(self.post("cancelled").status_code, 200)
        self.assertEqual(self.post("confirmed").status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "cancelled")

    def test_duplicate_is_acknowledged_once(self):
        self.assertEqual(self.post(event_id="same-event").status_code, 200)
        self.assertTrue(self.post(event_id="same-event").json()["duplicate"])
        self.assertEqual(ConnectorEvent.objects.count(), 1)

    def test_invalid_status_or_timestamp_is_not_accepted(self):
        self.assertEqual(self.post("paid").status_code, 422)
        self.assertEqual(self.post(timestamp="invalid").status_code, 422)
        self.assertFalse(ConnectorEvent.objects.exists())

    def test_cancelled_booking_is_not_dispatched_again(self):
        from django.core.management import call_command
        from unittest.mock import patch
        event = ConnectorEvent.objects.create(event_type="webhook.event", tenant=self.tenant, module=self.module, status="accepted")
        self.booking.connector_event = event
        self.booking.save()
        self.assertEqual(self.post("cancelled").status_code, 200)
        with patch("apps.connectors.management.commands.dispatch_marketplace_bookings.urlopen") as network:
            call_command("dispatch_marketplace_bookings")
            network.assert_not_called()
