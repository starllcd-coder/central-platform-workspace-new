from datetime import date, timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.ops.models import AuditLog
from apps.tenants.models import Module, Tenant

from .models import (
    AddOn,
    AddOnFeatureEntitlement,
    CommissionRule,
    Feature,
    Plan,
    PlanVersion,
    PricingTransition,
    SubscriptionInvoice,
    TenantAddOnSubscription,
    TenantSubscription,
)
from .services import apply_due_pricing_transitions, resolve_feature_for_tenant


class PricingRulesTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            tenant_code="T-STAYLUX",
            name="StayLux",
            owner_email="owner@staylux.test",
        )
        self.module = Module.objects.create(code="STAYLUX", name="StayLux")
        self.plan = Plan.objects.create(
            name="Starter",
            code="STARTER",
            billing_type="subscription",
            is_active=True,
        )

    def test_plan_version_overlap_is_rejected(self):
        PlanVersion.objects.create(
            plan=self.plan,
            version="v1",
            onboarding_fee=Decimal("10.00"),
            yearly_fee=Decimal("120.00"),
            commission_rate=Decimal("8.50"),
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 12, 31),
        )

        overlapping = PlanVersion(
            plan=self.plan,
            version="v2",
            onboarding_fee=Decimal("12.00"),
            yearly_fee=Decimal("130.00"),
            commission_rate=Decimal("9.00"),
            effective_from=date(2026, 6, 1),
            effective_to=date(2027, 5, 31),
        )

        with self.assertRaises(ValidationError):
            overlapping.full_clean()

    def test_commission_rule_overlap_is_rejected(self):
        CommissionRule.objects.create(
            tenant=self.tenant,
            module=self.module,
            booking_type="online",
            rate_percent=Decimal("12.50"),
            fixed_fee=Decimal("0.00"),
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 12, 31),
            is_active=True,
        )

        overlapping = CommissionRule(
            tenant=self.tenant,
            module=self.module,
            booking_type="online",
            rate_percent=Decimal("14.00"),
            fixed_fee=Decimal("0.00"),
            effective_from=date(2026, 6, 1),
            effective_to=date(2027, 3, 1),
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            overlapping.full_clean()

    def test_reconcile_subscriptions_cancels_expired_and_syncs_tenant(self):
        version = PlanVersion.objects.create(
            plan=self.plan,
            version="v2",
            onboarding_fee=Decimal("0.00"),
            yearly_fee=Decimal("120.00"),
            commission_rate=Decimal("10.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
        )
        self.tenant.pricing_model = "subscription"
        self.tenant.subscription_status = "active"
        self.tenant.save(update_fields=["pricing_model", "subscription_status", "updated_at"])
        sub = TenantSubscription.objects.create(
            tenant=self.tenant,
            plan_version=version,
            status="trial",
            start_date=timezone.localdate() - timedelta(days=40),
            end_date=timezone.localdate() - timedelta(days=1),
            pricing_version="v2",
        )

        call_command("reconcile_subscriptions")

        sub.refresh_from_db()
        self.tenant.refresh_from_db()
        self.assertEqual(sub.status, "cancelled")
        self.assertEqual(self.tenant.subscription_status, "inactive")
        self.assertTrue(
            AuditLog.objects.filter(
                action="pricing.subscription.expired",
                entity_type="TenantSubscription",
                entity_id=str(sub.id),
            ).exists()
        )

    def test_reconcile_subscriptions_dry_run_does_not_mutate(self):
        version = PlanVersion.objects.create(
            plan=self.plan,
            version="v2",
            onboarding_fee=Decimal("0.00"),
            yearly_fee=Decimal("120.00"),
            commission_rate=Decimal("10.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
        )
        sub = TenantSubscription.objects.create(
            tenant=self.tenant,
            plan_version=version,
            status="active",
            start_date=timezone.localdate() - timedelta(days=60),
            end_date=timezone.localdate() - timedelta(days=2),
            pricing_version="v2",
        )

        call_command("reconcile_subscriptions", "--dry-run")

        sub.refresh_from_db()
        self.assertEqual(sub.status, "active")

    def test_reconcile_subscriptions_creates_due_invoice(self):
        version = PlanVersion.objects.create(
            plan=self.plan,
            version="v2",
            onboarding_fee=Decimal("0.00"),
            yearly_fee=Decimal("150.00"),
            commission_rate=Decimal("10.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
        )
        self.tenant.pricing_model = "subscription"
        self.tenant.subscription_status = "active"
        self.tenant.save(update_fields=["pricing_model", "subscription_status", "updated_at"])
        sub = TenantSubscription.objects.create(
            tenant=self.tenant,
            plan_version=version,
            status="active",
            start_date=timezone.localdate() - timedelta(days=370),
            end_date=None,
            pricing_version="v2",
        )

        call_command("reconcile_subscriptions")

        invoice = SubscriptionInvoice.objects.filter(subscription=sub).first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.amount_due, Decimal("150.00"))

    def test_reconcile_subscriptions_marks_old_pending_invoice_overdue(self):
        version = PlanVersion.objects.create(
            plan=self.plan,
            version="v2",
            onboarding_fee=Decimal("0.00"),
            yearly_fee=Decimal("120.00"),
            commission_rate=Decimal("10.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
        )
        sub = TenantSubscription.objects.create(
            tenant=self.tenant,
            plan_version=version,
            status="active",
            start_date=timezone.localdate() - timedelta(days=800),
            end_date=None,
            pricing_version="v2",
        )
        invoice = SubscriptionInvoice.objects.create(
            tenant=self.tenant,
            subscription=sub,
            plan_version=version,
            invoice_code="SUB-TEST-OVERDUE-1",
            amount_due=Decimal("120.00"),
            currency="OMR",
            period_start=timezone.localdate() - timedelta(days=730),
            period_end=timezone.localdate() - timedelta(days=365),
            due_date=timezone.localdate() - timedelta(days=365),
            status="pending",
        )

        call_command("reconcile_subscriptions")

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "overdue")

    def test_pricing_transition_apply_due_creates_active_subscription(self):
        old_version = PlanVersion.objects.create(
            plan=self.plan,
            version="v1",
            onboarding_fee=Decimal("200.00"),
            yearly_fee=Decimal("0.00"),
            commission_rate=Decimal("0.00"),
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31),
        )
        new_version = PlanVersion.objects.create(
            plan=self.plan,
            version="v2",
            onboarding_fee=Decimal("0.00"),
            yearly_fee=Decimal("120.00"),
            commission_rate=Decimal("10.00"),
            effective_from=date(2026, 1, 1),
            effective_to=None,
        )
        TenantSubscription.objects.create(
            tenant=self.tenant,
            plan_version=old_version,
            status="active",
            start_date=date(2025, 1, 1),
            end_date=None,
            pricing_version="v1",
        )
        PricingTransition.objects.create(
            tenant=self.tenant,
            target_plan_version=new_version,
            effective_on=timezone.localdate(),
            status="scheduled",
        )

        result = apply_due_pricing_transitions(run_date=timezone.localdate(), limit=10)
        self.assertEqual(result["applied"], 1)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.pricing_version, "v2")
        self.assertEqual(self.tenant.subscription_status, "active")
        active = TenantSubscription.objects.filter(
            tenant=self.tenant,
            plan_version=new_version,
            status="active",
        ).first()
        self.assertIsNotNone(active)

    def test_feature_can_be_enabled_from_active_addon_entitlement(self):
        feature = Feature.objects.create(
            code="analytics.advanced",
            name="Advanced Analytics",
            default_enabled=False,
            is_active=True,
        )
        add_on = AddOn.objects.create(
            code="ADV_ANALYTICS",
            name="Advanced Analytics Add-on",
            billing_cycle="monthly",
            price=Decimal("25.00"),
            is_active=True,
        )
        AddOnFeatureEntitlement.objects.create(
            add_on=add_on,
            feature=feature,
            enabled=True,
        )
        TenantAddOnSubscription.objects.create(
            tenant=self.tenant,
            add_on=add_on,
            status="active",
            start_date=timezone.localdate() - timedelta(days=2),
            end_date=None,
        )

        resolved = resolve_feature_for_tenant(
            tenant=self.tenant,
            feature_code="analytics.advanced",
            default_if_missing=False,
        )
        self.assertTrue(resolved["enabled"])
        self.assertEqual(resolved["source"], "addon_entitlement")
