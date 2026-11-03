from datetime import date
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.pricing.models import CommissionRule
from apps.tenants.models import Module, Tenant

from .models import LedgerEntry, PaymentTransaction
from .services import enrich_and_post_transaction, resolve_commission_rate


class BillingServicesTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            tenant_code="T-DRIVESPHERE",
            name="DriveSphere",
            owner_email="owner@drivesphere.test",
        )
        self.module = Module.objects.create(code="DRIVESPHERE", name="DriveSphere")

    def test_resolve_commission_rate_prefers_more_specific_rule(self):
        CommissionRule.objects.create(
            tenant=None,
            module=None,
            booking_type="all",
            rate_percent=Decimal("5.00"),
            fixed_fee=Decimal("0.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
            is_active=True,
        )
        CommissionRule.objects.create(
            tenant=self.tenant,
            module=None,
            booking_type="all",
            rate_percent=Decimal("10.00"),
            fixed_fee=Decimal("0.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
            is_active=True,
        )
        CommissionRule.objects.create(
            tenant=self.tenant,
            module=self.module,
            booking_type="online",
            rate_percent=Decimal("15.00"),
            fixed_fee=Decimal("0.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
            is_active=True,
        )

        rate = resolve_commission_rate(
            tenant_id=self.tenant.id,
            module_id=self.module.id,
            booking_type="online",
            effective_date=date(2026, 4, 1),
        )
        self.assertEqual(rate, Decimal("15.00"))

    def test_enrich_and_post_transaction_generates_expected_ledger_rows(self):
        CommissionRule.objects.create(
            tenant=self.tenant,
            module=self.module,
            booking_type="online",
            rate_percent=Decimal("10.00"),
            fixed_fee=Decimal("0.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
            is_active=True,
        )
        tx = PaymentTransaction.objects.create(
            tenant=self.tenant,
            module=self.module,
            booking_ref="BK-1001",
            currency="OMR",
            payment_channel="online",
            status="paid",
            settlement_state="pending",
            booking_type="online",
            gross_amount=Decimal("100.00"),
            gateway_fee=Decimal("2.00"),
            tax_amount=Decimal("1.00"),
            occurred_at=timezone.now(),
        )

        enrich_and_post_transaction(tx)
        tx.refresh_from_db()

        self.assertEqual(tx.commission_rate, Decimal("10.00"))
        self.assertEqual(tx.commission_amount, Decimal("10.00"))
        self.assertEqual(tx.net_amount, Decimal("87.00"))
        self.assertEqual(tx.business_due_for_cash, Decimal("0.00"))
        self.assertEqual(
            LedgerEntry.objects.filter(transaction=tx).count(),
            4,
        )

    def test_enrich_and_post_transaction_rejects_demo_tenant(self):
        self.tenant.account_type = "demo"
        self.tenant.demo_expires_on = timezone.localdate() + timedelta(days=7)
        self.tenant.save(update_fields=["account_type", "demo_expires_on", "updated_at"])
        tx = PaymentTransaction.objects.create(
            tenant=self.tenant,
            module=self.module,
            booking_ref="BK-DEMO-1001",
            currency="OMR",
            payment_channel="online",
            status="paid",
            settlement_state="pending",
            booking_type="online",
            gross_amount=Decimal("100.00"),
            occurred_at=timezone.now(),
        )

        with self.assertRaisesMessage(ValueError, "demo sandbox"):
            enrich_and_post_transaction(tx)
