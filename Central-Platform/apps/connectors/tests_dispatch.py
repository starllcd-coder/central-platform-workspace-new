import json
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.connectors.models import AppConnector, ConnectorEvent
from apps.marketplace.models import MarketplaceBooking
from apps.tenants.models import MarketplaceListing, Module, Tenant


@override_settings(CONNECTOR_SHARED_SECRET="strong-test-connector-secret")
class MarketplaceDispatchTests(TestCase):
    def setUp(self):
        self.module = Module.objects.create(code="drivesphere", name="DriveSphere")
        self.tenant = Tenant.objects.create(tenant_code="DRV-ONE", name="Drive One", status="active")
        self.other_tenant = Tenant.objects.create(tenant_code="DRV-TWO", name="Drive Two", status="active")
        self.listing = MarketplaceListing.objects.create(
            tenant=self.tenant,
            module=self.module,
            base_price="20.00",
            provider_resource_id="CAR-1",
        )
        AppConnector.objects.create(module=self.module, tenant=self.tenant, base_url="https://drive-one.example")
        AppConnector.objects.create(module=self.module, tenant=self.other_tenant, base_url="https://drive-two.example")
        self.event = ConnectorEvent.objects.create(
            event_type="webhook.event",
            module=self.module,
            tenant=self.tenant,
            external_event_id="NXV-TEST-1",
            status="accepted",
            payload={
                "booking_id": "NXV-TEST-1",
                "tenant_code": self.tenant.tenant_code,
                "provider_resource_id": "CAR-1",
                "total_amount": "20.00",
                "payload": {"pickupDate": "2026-07-01", "returnDate": "2026-07-02"},
            },
        )
        self.booking = MarketplaceBooking.objects.create(
            booking_id="NXV-TEST-1",
            listing=self.listing,
            tenant=self.tenant,
            module=self.module,
            connector_event=self.event,
            fulfillment_status="connector_queued",
            total_amount="20.00",
        )

    @patch("apps.connectors.management.commands.dispatch_marketplace_bookings.urlopen")
    def test_dispatch_uses_tenant_url_and_signed_headers(self, mocked_urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps({"ok": True, "booking_id": 10}).encode()
        mocked_urlopen.return_value.__enter__.return_value = response

        call_command("dispatch_marketplace_bookings", limit=10)

        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://drive-one.example/api/central/bookings/")
        self.assertEqual(request.get_header("X-tenant-code"), "DRV-ONE")
        self.assertTrue(request.get_header("X-connector-signature"))
        self.booking.refresh_from_db()
        self.event.refresh_from_db()
        self.assertEqual(self.booking.fulfillment_status, "provider_confirmed")
        self.assertEqual(self.event.status, "dispatched")

    @patch("apps.connectors.management.commands.dispatch_marketplace_bookings.urlopen")
    def test_failure_is_retryable(self, mocked_urlopen):
        mocked_urlopen.side_effect = OSError("provider offline")
        call_command("dispatch_marketplace_bookings", limit=10)
        self.event.refresh_from_db()
        self.booking.refresh_from_db()
        self.assertEqual(self.event.status, "dispatch_failed")
        self.assertEqual(self.event.dispatch_attempts, 1)
        self.assertIsNotNone(self.event.next_retry_at)
        self.assertEqual(self.booking.fulfillment_status, "connector_queued")

    @patch("apps.connectors.management.commands.dispatch_marketplace_bookings.urlopen")
    def test_unexpired_claim_is_not_dispatched(self, mocked):
        from datetime import timedelta
        from django.utils import timezone
        self.event.status = "dispatching"
        self.event.next_retry_at = timezone.now() + timedelta(minutes=5)
        self.event.save()
        call_command("dispatch_marketplace_bookings")
        mocked.assert_not_called()

    @patch("apps.connectors.management.commands.dispatch_marketplace_bookings.urlopen")
    def test_abandoned_claim_is_retried(self, mocked):
        from datetime import timedelta
        from django.utils import timezone
        self.event.status = "dispatching"
        self.event.next_retry_at = timezone.now() - timedelta(seconds=1)
        self.event.save()
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"ok":true}'
        mocked.return_value.__enter__.return_value = response
        call_command("dispatch_marketplace_bookings")
        mocked.assert_called_once()
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, "dispatched")
