from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.stay.models import StayBooking, StayUnitRate
from apps.stay.services import create_stay_booking, extend_stay_booking
from apps.tenants.models import Branch, Module, Tenant, Unit


class StayExtensionTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            tenant_code="T-STAY",
            name="Stay Tenant",
            owner_email="owner@stay.test",
            module_type="staylux",
        )
        self.module = Module.objects.create(code="STAYLUX", name="StayLux")
        self.branch = Branch.objects.create(tenant=self.tenant, code="BR-1", name="Main")
        self.unit1 = Unit.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            code="U-101",
            name="Unit 101",
            unit_type="standard",
            capacity=2,
        )
        self.unit2 = Unit.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            code="U-102",
            name="Unit 102",
            unit_type="standard",
            capacity=2,
        )
        for day in [date(2026, 5, 1), date(2026, 5, 2), date(2026, 5, 3), date(2026, 5, 4), date(2026, 5, 5)]:
            StayUnitRate.objects.create(
                tenant=self.tenant,
                unit=self.unit1,
                day=day,
                nightly_rate=Decimal("20.00"),
                currency="OMR",
            )
            StayUnitRate.objects.create(
                tenant=self.tenant,
                unit=self.unit2,
                day=day,
                nightly_rate=Decimal("25.00"),
                currency="OMR",
            )

    def test_extension_creates_linked_booking_and_keeps_original_unchanged(self):
        original = create_stay_booking(
            tenant=self.tenant,
            unit=self.unit1,
            check_in=date(2026, 5, 1),
            check_out=date(2026, 5, 3),
            payment_rule="pay_at_property",
            customer_name="Sara",
            customer_email="sara@test.com",
        )
        extension, _preview = extend_stay_booking(
            parent_booking=original,
            new_check_out=date(2026, 5, 5),
            payment_rule="pay_now",
        )
        original.refresh_from_db()
        self.assertEqual(original.check_out.isoformat(), "2026-05-03")
        self.assertEqual(extension.parent_booking_id, original.id)
        self.assertEqual(extension.booking_type, "extension")
        self.assertEqual(extension.check_in.isoformat(), "2026-05-03")
        self.assertEqual(extension.check_out.isoformat(), "2026-05-05")
        self.assertIsNotNone(extension.commission_record)
        self.assertEqual(extension.payment_status, "paid")

    def test_extension_switches_to_alternative_when_same_unit_unavailable(self):
        original = create_stay_booking(
            tenant=self.tenant,
            unit=self.unit1,
            check_in=date(2026, 5, 1),
            check_out=date(2026, 5, 3),
            payment_rule="pay_at_property",
            customer_name="Ali",
            customer_email="ali@test.com",
        )
        StayBooking.objects.create(
            tenant=self.tenant,
            module=self.module,
            unit=self.unit1,
            booking_id="SB-BLOCK",
            booking_type="original",
            customer_name="Blocker",
            customer_email="block@test.com",
            check_in=date(2026, 5, 3),
            check_out=date(2026, 5, 5),
            guests=1,
            payment_rule="pay_at_property",
            payment_status="due_at_property",
            currency="OMR",
            subtotal_amount=Decimal("40.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("40.00"),
            status="confirmed",
        )
        extension, _preview = extend_stay_booking(
            parent_booking=original,
            new_check_out=date(2026, 5, 5),
            payment_rule="add_to_existing_bill",
        )
        self.assertEqual(extension.unit_id, self.unit2.id)
        self.assertEqual(extension.billed_to_booking_id, original.id)
        self.assertEqual(extension.payment_status, "added_to_bill")

    def test_customer_dashboard_ignores_another_customer_email(self):
        own_booking = create_stay_booking(
            tenant=self.tenant,
            unit=self.unit1,
            check_in=date(2026, 5, 1),
            check_out=date(2026, 5, 2),
            payment_rule="pay_at_property",
            customer_name="Customer",
            customer_email="customer@test.com",
        )
        other_booking = create_stay_booking(
            tenant=self.tenant,
            unit=self.unit2,
            check_in=date(2026, 5, 1),
            check_out=date(2026, 5, 2),
            payment_rule="pay_at_property",
            customer_name="Other",
            customer_email="other@test.com",
        )
        user = get_user_model().objects.create_user(
            username="customer@test.com",
            email="customer@test.com",
            password="Pass12345!",
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse("stay-customer-dashboard"),
            {"customer_email": "other@test.com"},
        )

        self.assertContains(response, own_booking.booking_id)
        self.assertNotContains(response, other_booking.booking_id)
