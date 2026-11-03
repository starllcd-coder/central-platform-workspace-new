import json
import hashlib
import hmac
import time

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.marketplace.models import MarketplaceBooking
from apps.connectors.models import ConnectorEvent
from apps.tenants.models import Branch, DemoTenantRequest, MarketplaceListing, Module, Tenant, TenantModule, Unit


class MarketplaceBookingApiTests(TestCase):
    def setUp(self):
        self.stay_module = Module.objects.create(code="staylux", name="StayLux")
        self.drive_module = Module.objects.create(code="drivesphere", name="DriveSphere")
        self.stay_tenant = Tenant.objects.create(
            tenant_code="TNT-STAY-TEST",
            name="Stay Tenant",
            status="active",
            currency="OMR",
        )
        self.drive_tenant = Tenant.objects.create(
            tenant_code="TNT-DRV-TEST",
            name="Drive Tenant",
            status="active",
            currency="OMR",
        )
        TenantModule.objects.create(
            tenant=self.stay_tenant,
            module=self.stay_module,
            enabled=True,
            marketplace_enabled=True,
        )
        TenantModule.objects.create(
            tenant=self.drive_tenant,
            module=self.drive_module,
            enabled=True,
            marketplace_enabled=True,
        )
        branch = Branch.objects.create(tenant=self.stay_tenant, code="BR1", name="Main")
        Unit.objects.create(tenant=self.stay_tenant, branch=branch, code="U1", name="Unit 1", status="active")
        MarketplaceListing.objects.create(
            tenant=self.stay_tenant,
            module=self.stay_module,
            base_price="25.00",
            provider_resource_id="U1",
            provider_resource_name="Unit 1",
        )
        MarketplaceListing.objects.create(
            tenant=self.drive_tenant,
            module=self.drive_module,
            base_price="15.00",
            provider_resource_id="CAR-1",
            provider_resource_name="Test Car",
        )

    @override_settings(PAYMENT_GATEWAY_MODE="disabled")
    def test_unconfigured_checkout_does_not_return_a_fake_session(self):
        response = self.client.post(reverse("marketplace-api-payments-session"), data="{}", content_type="application/json")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("sessionId", response.json())

    @override_settings(PAYMENT_GATEWAY_MODE="disabled")
    def test_online_booking_does_not_bypass_checkout(self):
        response = self.client.post(reverse("marketplace-api-bookings"), data=json.dumps({"paymentMethod": "pay-online"}), content_type="application/json")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(MarketplaceBooking.objects.count(), 0)

    @override_settings(PAYMENT_GATEWAY_MODE="mock")
    def test_test_checkout_is_explicitly_simulated(self):
        response = self.client.post(reverse("marketplace-api-payments-session"), data=json.dumps({"amount": "30.00"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["testMode"])
        self.assertFalse(response.json()["charged"])

    @override_settings(PAYMENT_GATEWAY_MODE="mock")
    def test_online_test_booking_is_persisted_without_marking_paid(self):
        response = self.client.post(reverse("marketplace-api-bookings"), data=json.dumps({
            "listingSlug": "drive-tenant-drivesphere-2", "fullName": "Customer", "email": "customer@example.com",
            "pickupDate": "2026-07-01", "returnDate": "2026-07-04", "paymentMethod": "pay-online",
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MarketplaceBooking.objects.get().payment_status, "test_unpaid")

    def test_guest_confirmation_requires_signed_link_and_hides_contact_details(self):
        from django.core import signing
        booking = MarketplaceBooking.objects.create(booking_id="NXV-GUEST", tenant=self.drive_tenant, module=self.drive_module, customer_email="private@example.com")
        token = signing.dumps({"booking_id": booking.booking_id}, salt="marketplace-confirmation-v1")
        url = reverse("marketplace-booking-confirmation")
        self.assertEqual(self.client.get(url, {"token": "invalid"}).status_code, 401)
        response = self.client.get(url, {"token": token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["bookingId"], booking.booking_id)
        self.assertNotIn("private@example.com", response.content.decode())
        self.assertNotIn("customer_email", response.json())

    def test_browser_total_cannot_override_listing_price(self):
        response = self.client.post(reverse("marketplace-api-bookings"), data=json.dumps({
            "listingSlug": "drive-tenant-drivesphere-2", "fullName": "Customer", "email": "customer@example.com",
            "pickupDate": "2026-07-01", "returnDate": "2026-07-04", "estimatedTotal": "0.01",
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MarketplaceBooking.objects.get().total_amount, 45)

    def test_staylux_booking_creates_marketplace_and_stay_record(self):
        response = self.client.post(
            reverse("marketplace-api-bookings"),
            data=json.dumps(
                {
                    "listingSlug": "stay-tenant-staylux-1",
                    "fullName": "Test Customer",
                    "email": "customer@example.com",
                    "checkIn": "2026-07-01",
                    "checkOut": "2026-07-03",
                    "estimatedTotal": "50.00",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["moduleCode"], "staylux")
        self.assertEqual(payload["status"], "confirmed")
        self.assertEqual(payload["fulfillmentStatus"], "central_confirmed")
        self.assertEqual(MarketplaceBooking.objects.count(), 1)
        self.assertIsNotNone(MarketplaceBooking.objects.first().stay_booking)

    def test_drivesphere_booking_creates_queued_marketplace_record(self):
        response = self.client.post(
            reverse("marketplace-api-bookings"),
            data=json.dumps(
                {
                    "listingSlug": "drive-tenant-drivesphere-2",
                    "fullName": "Test Customer",
                    "email": "customer@example.com",
                    "pickupDate": "2026-07-01",
                    "returnDate": "2026-07-03",
                    "estimatedTotal": "30.00",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["moduleCode"], "drivesphere")
        self.assertEqual(payload["status"], "pending")
        self.assertEqual(payload["fulfillmentStatus"], "connector_queued")
        booking = MarketplaceBooking.objects.get(booking_id=payload["bookingId"])
        self.assertIsNotNone(booking.connector_event)

    def test_idempotency_key_returns_existing_booking(self):
        headers = {"HTTP_X_IDEMPOTENCY_KEY": "idem-1"}
        body = {
            "listingSlug": "drive-tenant-drivesphere-2",
            "fullName": "Test Customer",
            "email": "customer@example.com",
            "pickupDate": "2026-07-01",
            "returnDate": "2026-07-03",
            "estimatedTotal": "30.00",
        }

        first = self.client.post(
            reverse("marketplace-api-bookings"),
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )
        second = self.client.post(
            reverse("marketplace-api-bookings"),
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.json()["duplicate"])
        self.assertEqual(MarketplaceBooking.objects.count(), 1)

    def test_booking_references_do_not_collide_for_same_tenant(self):
        body = {
            "listingSlug": "drive-tenant-drivesphere-2",
            "fullName": "Test Customer",
            "email": "customer@example.com",
            "pickupDate": "2026-07-01",
            "returnDate": "2026-07-03",
            "estimatedTotal": "30.00",
        }
        first = self.client.post(reverse("marketplace-api-bookings"), data=json.dumps(body), content_type="application/json")
        second = self.client.post(reverse("marketplace-api-bookings"), data=json.dumps(body), content_type="application/json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertNotEqual(first.json()["bookingId"], second.json()["bookingId"])

    def test_finalize_requires_webhook_secret(self):
        response = self.client.post(
            reverse("marketplace-api-bookings-finalize"),
            data=json.dumps({"bookingId": "missing", "paymentStatus": "paid"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_provider_login_returns_admin_role_for_superuser(self):
        get_user_model().objects.create_superuser(
            username="admin@test.com",
            email="admin@test.com",
            password="Pass12345!",
        )

        response = self.client.post(
            reverse("marketplace-api-provider-login"),
            data=json.dumps({"email": "admin@test.com", "password": "Pass12345!"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["role"], "admin")

    def _post_nexivo_demo_request(self, payload, *, reference="nexivo-lead-001", signed=True):
        path = reverse("marketplace-api-leads")
        body = json.dumps(payload)
        timestamp = str(int(time.time()))
        headers = {"HTTP_X_IDEMPOTENCY_KEY": reference}
        if signed:
            headers.update(
                {
                    "HTTP_X_NEXIVO_TIMESTAMP": timestamp,
                    "HTTP_X_NEXIVO_SIGNATURE": hmac.new(
                        b"dev-nexivo-lead-secret",
                        f"{timestamp}.{reference}.".encode() + body.encode(),
                        hashlib.sha256,
                    ).hexdigest(),
                }
            )
        return self.client.post(
            path,
            data=body,
            content_type="application/json",
            **headers,
        )

    def test_nexivo_demo_lead_creates_pending_demo_request(self):
        response = self._post_nexivo_demo_request(
            {
                "fullName": "Nexivo Owner",
                "businessName": "Nexivo Hotel",
                "email": "owner@nexivo-hotel.test",
                "phone": "+96890000000",
                "country": "OM",
                "city": "Muscat",
                "productInterest": "staylux",
                "businessType": "Hotel",
                "estimatedSize": "medium",
                "message": "We need a property demo.",
            }
        )

        self.assertEqual(response.status_code, 201)
        row = DemoTenantRequest.objects.get(source="nexivo", external_reference="nexivo-lead-001")
        self.assertEqual(row.status, "requested")
        self.assertEqual(row.product_interest, "staylux")
        self.assertEqual(row.module_type, "staylux")
        self.assertEqual(row.currency, "OMR")
        self.assertIn("Muscat", row.request_notes)
        event = ConnectorEvent.objects.get(external_event_id="nexivo-lead-001")
        self.assertEqual(event.payload["demo_request_id"], row.id)
        self.assertEqual(response.json()["demoRequestId"], row.id)

    def test_nexivo_demo_lead_requires_valid_signature(self):
        response = self._post_nexivo_demo_request({}, signed=False)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(DemoTenantRequest.objects.count(), 0)

    def test_nexivo_demo_lead_is_idempotent(self):
        payload = {
            "fullName": "Fleet Owner",
            "businessName": "Nexivo Fleet",
            "email": "owner@nexivo-fleet.test",
            "phone": "+971500000001",
            "country": "AE",
            "city": "Dubai",
            "productInterest": "drivesphere",
            "businessType": "Car Rental Company",
            "estimatedSize": "small",
        }
        first = self._post_nexivo_demo_request(payload, reference="nexivo-lead-idempotent")
        second = self._post_nexivo_demo_request(payload, reference="nexivo-lead-idempotent")

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.json()["duplicate"])
        self.assertEqual(
            DemoTenantRequest.objects.filter(external_reference="nexivo-lead-idempotent").count(), 1
        )
        self.assertEqual(
            ConnectorEvent.objects.filter(external_event_id="nexivo-lead-idempotent").count(), 1
        )

    def test_multiple_product_lead_requires_staff_module_selection_on_approval(self):
        response = self._post_nexivo_demo_request(
            {
                "fullName": "Group Owner",
                "businessName": "Nexivo Group",
                "email": "owner@nexivo-group.test",
                "phone": "+97330000000",
                "country": "BH",
                "city": "Manama",
                "productInterest": "multiple",
                "businessType": "Multi-service Business",
                "estimatedSize": "enterprise",
            },
            reference="nexivo-lead-multiple",
        )
        row = DemoTenantRequest.objects.get(pk=response.json()["demoRequestId"])
        self.assertEqual(row.module_type, "")

        staff = get_user_model().objects.create_superuser(
            username="nexivo-approver",
            email="approver@example.test",
            password="Pass12345!",
        )
        self.client.force_login(staff)
        approval = self.client.post(
            reverse("demo-request-review", args=[row.id]),
            {"action": "approve", "module_type": "laundrex", "review_notes": "Approved"},
        )

        self.assertRedirects(approval, reverse("demo-request-list"))
        row.refresh_from_db()
        self.assertEqual(row.status, "approved")
        self.assertEqual(row.product_interest, "multiple")
        self.assertEqual(row.module_type, "laundrex")
        self.assertEqual(row.approved_tenant.module_type, "laundrex")
