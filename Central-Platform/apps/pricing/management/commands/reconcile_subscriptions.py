from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.ops.services import log_audit
from apps.tenants.policies import sync_tenant_subscription_status

from apps.pricing.models import SubscriptionInvoice, TenantSubscription


def _add_years_safe(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        # Handle leap day rollover.
        return day.replace(month=2, day=28, year=day.year + years)


class Command(BaseCommand):
    help = (
        "Reconcile subscription lifecycle by cancelling expired subscriptions and "
        "syncing tenant subscription_status. Also creates due yearly invoices."
    )

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=500)
        parser.add_argument("--dry-run", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        limit = max(1, int(options["limit"]))
        dry_run = options["dry_run"]

        qs = (
            TenantSubscription.objects.select_related("tenant")
            .filter(status__in=["trial", "active"], end_date__isnull=False, end_date__lt=today)
            .order_by("end_date", "id")
        )
        rows = list(qs[:limit])

        cancelled_count = 0
        tenant_ids = set()
        for sub in rows:
            tenant_ids.add(sub.tenant_id)
            if dry_run:
                continue
            previous = sub.status
            sub.status = "cancelled"
            sub.save(update_fields=["status"])
            cancelled_count += 1
            log_audit(
                actor=None,
                tenant=sub.tenant,
                action="pricing.subscription.expired",
                entity_type="TenantSubscription",
                entity_id=sub.id,
                metadata={
                    "previous_status": previous,
                    "new_status": sub.status,
                    "end_date": sub.end_date.isoformat() if sub.end_date else "",
                },
            )

        synced_tenants = 0
        if not dry_run:
            tenant_map = {}
            for sub in rows:
                tenant_map[sub.tenant_id] = sub.tenant
            for tenant_id in tenant_ids:
                tenant = tenant_map[tenant_id]
                sync_tenant_subscription_status(tenant)
                synced_tenants += 1

        due_subscriptions = list(
            TenantSubscription.objects.select_related("tenant", "plan_version", "plan_version__plan")
            .filter(
                status__in=["active", "trial"],
                start_date__lte=today,
                plan_version__plan__billing_type="subscription",
                plan_version__yearly_fee__gt=0,
            )
            .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
            .order_by("start_date", "id")[:limit]
        )

        invoices_created = 0
        invoices_overdue = 0
        for sub in due_subscriptions:
            years_elapsed = max(0, today.year - sub.start_date.year)
            period_start = _add_years_safe(sub.start_date, years_elapsed)
            if period_start > today:
                years_elapsed = max(0, years_elapsed - 1)
                period_start = _add_years_safe(sub.start_date, years_elapsed)
            period_end = _add_years_safe(period_start, 1)

            existing = SubscriptionInvoice.objects.filter(
                subscription=sub,
                period_start=period_start,
                period_end=period_end,
            ).first()
            if existing is None:
                if dry_run:
                    continue
                code = f"SUB-{sub.tenant.tenant_code}-{sub.id}-{period_start.strftime('%Y%m%d')}"
                invoice = SubscriptionInvoice.objects.create(
                    tenant=sub.tenant,
                    subscription=sub,
                    plan_version=sub.plan_version,
                    invoice_code=code[:50],
                    amount_due=sub.plan_version.yearly_fee,
                    currency=sub.tenant.currency or "OMR",
                    period_start=period_start,
                    period_end=period_end,
                    due_date=period_start,
                    status="pending",
                    metadata={"source": "reconcile_subscriptions"},
                )
                invoices_created += 1
                log_audit(
                    actor=None,
                    tenant=sub.tenant,
                    action="pricing.subscription.invoice.created",
                    entity_type="SubscriptionInvoice",
                    entity_id=invoice.id,
                    metadata={
                        "subscription_id": sub.id,
                        "period_start": period_start.isoformat(),
                        "period_end": period_end.isoformat(),
                        "amount_due": str(sub.plan_version.yearly_fee),
                    },
                )

        overdue_qs = SubscriptionInvoice.objects.filter(status="pending", due_date__lt=today).order_by("due_date", "id")
        overdue_rows = list(overdue_qs[:limit])
        for invoice in overdue_rows:
            if dry_run:
                continue
            invoice.status = "overdue"
            invoice.save(update_fields=["status", "updated_at"])
            invoices_overdue += 1
            log_audit(
                actor=None,
                tenant=invoice.tenant,
                action="pricing.subscription.invoice.overdue",
                entity_type="SubscriptionInvoice",
                entity_id=invoice.id,
                metadata={"due_date": invoice.due_date.isoformat()},
            )

        self.stdout.write(
            f"reconcile_subscriptions dry_run={dry_run} considered={len(rows)} "
            f"cancelled={cancelled_count} tenants_synced={synced_tenants} "
            f"invoices_created={invoices_created} invoices_marked_overdue={invoices_overdue}"
        )
