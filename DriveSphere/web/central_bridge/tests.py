import hashlib
import hmac
import json
import time
import uuid
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Delivery

@override_settings(CENTRAL_CONNECTOR_SECRET="test-strong-secret", CENTRAL_TENANT_CODE="TENANT-ONE")
class BookingReceiverTests(TestCase):
    def post(self, body=None, tenant="TENANT-ONE", nonce=None, endpoint="central-booking-receiver"):
        body = body or self.envelope
        raw = json.dumps(body).encode()
        timestamp = str(int(time.time()))
        nonce = nonce or uuid.uuid4().hex
        signature = hmac.new(b"test-strong-secret", f"{timestamp}.{nonce}.".encode() + raw, hashlib.sha256).hexdigest()
        return self.client.post(reverse(endpoint), raw, content_type="application/json",
            HTTP_X_CONNECTOR_SECRET="test-strong-secret", HTTP_X_TENANT_CODE=tenant,
            HTTP_X_CONNECTOR_TIMESTAMP=timestamp, HTTP_X_CONNECTOR_NONCE=nonce,
            HTTP_X_CONNECTOR_SIGNATURE=signature)

    def test_signed_booking_is_persisted_and_duplicate_is_safe(self):
        response = self.post()
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(self.post().json()["duplicate"], True)
        self.assertEqual(Delivery.objects.count(), 1)
        self.assertEqual(self.booking_model.objects.count(), 1)
        self.assertEqual(str(self.booking_model.objects.get().total_amount if hasattr(self.booking_model, "total_amount") else self.booking_model.objects.get().locked_total), "40.000")

    def test_tenant_and_signature_required(self):
        self.assertEqual(self.post(tenant="OTHER").status_code, 403)
        self.assertEqual(self.client.post(reverse("central-booking-receiver"), "{}", content_type="application/json").status_code, 403)
        self.assertEqual(self.booking_model.objects.count(), 0)

    def test_nonce_cannot_be_replayed(self):
        self.assertEqual(self.post(nonce="same-nonce").status_code, 201)
        self.assertEqual(self.post(nonce="same-nonce").status_code, 403)

    def test_overlap_and_stale_price_are_rejected_without_side_effects(self):
        self.assertEqual(self.post().status_code, 201)
        other = {**self.envelope, "booking_id": "NXV-SECOND"}
        self.assertEqual(self.post(other).status_code, 422)
        other = {**self.envelope, "booking_id": "NXV-THIRD", "total_amount": "1.00"}
        self.assertEqual(self.post(other).status_code, 422)
        self.assertEqual(Delivery.objects.count(), 1)
        self.assertEqual(self.booking_model.objects.count(), 1)

    def test_conflicting_id_is_rejected(self):
        self.assertEqual(self.post().status_code, 201)
        other = {**self.envelope, "total_amount": "60.00"}
        self.assertEqual(self.post(other).status_code, 409)

    def test_status_save_queues_event_without_changing_booking_fields(self):
        from central_sync.models import OutboundEvent
        self.assertEqual(self.post().status_code, 201)
        booking = self.booking_model.objects.get()
        with override_settings(CENTRAL_SYNC_ENABLED=True):
            booking.status = 'CANCELLED'
            booking.save(update_fields=["status", "updated_at"])
        event = OutboundEvent.objects.get()
        self.assertEqual(event.payload["data"]["booking_id"], "NXV-ONE")
        self.assertEqual(event.payload["data"]["status"], "cancelled")
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')

    def test_inventory_publication_preserves_provider_resource_values(self):
        from central_sync.models import OutboundEvent
        from apps.fleet.models import Vehicle
        resource=Vehicle.objects.get()
        with override_settings(CENTRAL_SYNC_ENABLED=True):
            resource.save()
        event=OutboundEvent.objects.filter(payload__event_name="marketplace.resource.updated").last()
        self.assertIsNotNone(event)
        self.assertEqual(event.payload["data"]["resource_id"],str(resource.pk))
        self.assertEqual(event.payload["data"]["base_price"],"20.000")

    def test_verified_payment_and_refund_are_idempotent_native_records(self):
        from central_sync.models import PaymentDelivery
        self.assertEqual(self.post().status_code,201)
        payload={"tenant_code":"TENANT-ONE","module_code":self.envelope["module_code"],"booking_id":"NXV-ONE",
            "external_event_id":"pay-one","payment_id":"pay-one","kind":"payment","amount":"40.000","currency":"OMR"}
        response=self.post(payload,endpoint="central-payments")
        self.assertEqual(response.status_code,200,response.content)
        self.assertTrue(self.post(payload,endpoint="central-payments").json()["duplicate"])
        refund={**payload,"external_event_id":"refund-one","kind":"refund","amount":"20.000"}
        response=self.post(refund,endpoint="central-payments")
        self.assertEqual(response.status_code,200,response.content)
        self.assertEqual(PaymentDelivery.objects.count(),2)

    def setUp(self):
        from apps.fleet.models import Vehicle, VehicleBrand, VehicleModel
        from apps.bookings.models import Booking
        self.booking_model = Booking
        brand = VehicleBrand.objects.create(name="Test")
        model = VehicleModel.objects.create(brand=brand, name="Car")
        vehicle = Vehicle.objects.create(brand=brand, model=model, plate_number="CAR-ONE", year=2026, daily_rate="20")
        self.envelope = {"booking_id": "NXV-ONE", "tenant_code": "TENANT-ONE", "module_code": "drivesphere",
            "provider_resource_id": str(vehicle.pk), "total_amount": "40.00", "currency": "OMR",
            "payload": {"fullName": "Customer", "email": "customer@example.com", "pickupDate": "2027-01-01", "returnDate": "2027-01-03"}}


@override_settings(CENTRAL_CONNECTOR_SECRET="test-strong-secret", CENTRAL_CONNECTOR_SIGNED=True)
class OutboundSigningTests(TestCase):
    def test_signature_uses_timestamp_nonce_and_raw_body(self):
        from apps.core.central_connector import _connector_headers
        body = b'{"tenant_code":"TENANT-ONE"}'
        headers = _connector_headers(body)
        signed = f"{headers['X-Connector-Timestamp']}.{headers['X-Connector-Nonce']}.".encode() + body
        expected = hmac.new(b"test-strong-secret", signed, hashlib.sha256).hexdigest()
        self.assertEqual(headers["X-Connector-Signature"], expected)
        self.assertNotEqual(headers["X-Connector-Nonce"], _connector_headers(body)["X-Connector-Nonce"])
