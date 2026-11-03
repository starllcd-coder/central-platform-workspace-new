from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncHour
from django.utils import timezone

from apps.billing.models import DisputeCase, PaymentTransaction, RefundRecord, Settlement, WalletAccount, WithdrawalRequest
from apps.connectors.models import ConnectorHealthLog
from apps.stay.models import StayBooking
from apps.tenants.models import TenantModule

from .models import NotificationEvent, OccupancySnapshot


def filter_date_range(qs, date_field, start, end):
    if start:
        qs = qs.filter(**{f"{date_field}__date__gte": start})
    if end:
        qs = qs.filter(**{f"{date_field}__date__lte": end})
    return qs


def filter_date_range_datefield(qs, date_field, start, end):
    if start:
        qs = qs.filter(**{f"{date_field}__gte": start})
    if end:
        qs = qs.filter(**{f"{date_field}__lte": end})
    return qs


def build_analytics_snapshot(*, tenant_id=None, scoped_tenant_filter=None, module_id=None, start=None, end=None):
    tx = PaymentTransaction.objects.filter(status="paid")
    refunds = RefundRecord.objects.all()
    settlements = Settlement.objects.all()
    disputes = DisputeCase.objects.all()
    occupancy = OccupancySnapshot.objects.all()
    stay_bookings = StayBooking.objects.all()

    if tenant_id:
        tx = tx.filter(tenant_id=tenant_id)
        refunds = refunds.filter(transaction__tenant_id=tenant_id)
        settlements = settlements.filter(tenant_id=tenant_id)
        disputes = disputes.filter(tenant_id=tenant_id)
        occupancy = occupancy.filter(tenant_id=tenant_id)
        stay_bookings = stay_bookings.filter(tenant_id=tenant_id)
    elif scoped_tenant_filter is not None:
        tx = tx.filter(tenant_id__in=scoped_tenant_filter)
        refunds = refunds.filter(transaction__tenant_id__in=scoped_tenant_filter)
        settlements = settlements.filter(tenant_id__in=scoped_tenant_filter)
        disputes = disputes.filter(tenant_id__in=scoped_tenant_filter)
        occupancy = occupancy.filter(tenant_id__in=scoped_tenant_filter)
        stay_bookings = stay_bookings.filter(tenant_id__in=scoped_tenant_filter)

    if module_id:
        tx = tx.filter(module_id=module_id)
        refunds = refunds.filter(transaction__module_id=module_id)
        disputes = disputes.filter(transaction__module_id=module_id)
        occupancy = occupancy.filter(module_id=module_id)
        stay_bookings = stay_bookings.filter(module_id=module_id)

    tx = filter_date_range(tx, "occurred_at", start, end)
    refunds = filter_date_range(refunds, "created_at", start, end)
    settlements = filter_date_range(settlements, "created_at", start, end)
    disputes = filter_date_range(disputes, "opened_at", start, end)
    occupancy = filter_date_range_datefield(occupancy, "snapshot_date", start, end)
    stay_bookings = filter_date_range(stay_bookings, "created_at", start, end)

    totals = tx.aggregate(gross=Sum("gross_amount"), commission=Sum("commission_amount"), net=Sum("net_amount"), tx_count=Count("id"))
    refund_totals = refunds.aggregate(refund_amount=Sum("customer_refund_amount"), refund_count=Count("id"))
    settlement_totals = settlements.aggregate(payout_total=Sum("net_payout"), settlement_count=Count("id"))
    dispute_counts = list(disputes.values("status").annotate(count=Count("id")).order_by("status"))
    occupancy_totals = occupancy.aggregate(
        total_units_sum=Sum("total_units"),
        occupied_units_sum=Sum("occupied_units"),
        total_capacity_sum=Sum("total_capacity"),
        used_capacity_sum=Sum("used_capacity"),
        snapshot_days=Count("id"),
    )
    total_units_sum = occupancy_totals.get("total_units_sum") or 0
    occupied_units_sum = occupancy_totals.get("occupied_units_sum") or 0
    total_capacity_sum = occupancy_totals.get("total_capacity_sum") or 0
    used_capacity_sum = occupancy_totals.get("used_capacity_sum") or 0
    occupancy_rate_pct = round((occupied_units_sum / total_units_sum) * 100, 2) if total_units_sum else 0
    utilization_rate_pct = round((used_capacity_sum / total_capacity_sum) * 100, 2) if total_capacity_sum else 0
    stay_totals = stay_bookings.aggregate(
        stay_revenue_total=Sum("total_amount"),
        stay_original_revenue=Sum("total_amount", filter=Q(booking_type="original")),
        stay_extension_revenue=Sum("total_amount", filter=Q(booking_type="extension")),
        stay_extension_count=Count("id", filter=Q(booking_type="extension")),
    )
    daily_revenue = list(
        tx.values("occurred_at__date")
        .annotate(gross=Sum("gross_amount"), commission=Sum("commission_amount"), net=Sum("net_amount"))
        .order_by("occurred_at__date")[:60]
    )
    top_tenants = list(tx.values("tenant__name").annotate(gross=Sum("gross_amount"), tx_count=Count("id")).order_by("-gross")[:10])

    wallet_scope = WalletAccount.objects.all()
    withdrawal_scope = WithdrawalRequest.objects.all()
    if tenant_id:
        wallet_scope = wallet_scope.filter(tenant_id=tenant_id)
        withdrawal_scope = withdrawal_scope.filter(tenant_id=tenant_id)
    elif scoped_tenant_filter is not None:
        wallet_scope = wallet_scope.filter(tenant_id__in=scoped_tenant_filter)
        withdrawal_scope = withdrawal_scope.filter(tenant_id__in=scoped_tenant_filter)
    withdrawal_scope = filter_date_range(withdrawal_scope, "requested_at", start, end)
    wallet_totals = wallet_scope.aggregate(wallet_available_total=Sum("available_balance"), wallet_pending_total=Sum("pending_balance"))

    marketplace_scope = TenantModule.objects.filter(enabled=True, marketplace_enabled=True)
    if tenant_id:
        marketplace_scope = marketplace_scope.filter(tenant_id=tenant_id)
    elif scoped_tenant_filter is not None:
        marketplace_scope = marketplace_scope.filter(tenant_id__in=scoped_tenant_filter)
    if module_id:
        marketplace_scope = marketplace_scope.filter(module_id=module_id)
    today = timezone.localdate()

    health_since = timezone.now() - timezone.timedelta(hours=24)
    connector_health = ConnectorHealthLog.objects.filter(created_at__gte=health_since)
    notifications_health = NotificationEvent.objects.filter(created_at__gte=health_since)
    if tenant_id:
        connector_health = connector_health.filter(tenant_id=tenant_id)
        notifications_health = notifications_health.filter(tenant_id=tenant_id)
    elif scoped_tenant_filter is not None:
        connector_health = connector_health.filter(tenant_id__in=scoped_tenant_filter)
        notifications_health = notifications_health.filter(tenant_id__in=scoped_tenant_filter)
    if module_id:
        connector_health = connector_health.filter(module_id=module_id)
        notifications_health = notifications_health.filter(module_id=module_id)

    connector_success_count = connector_health.filter(is_success=True).count()
    connector_failure_count = connector_health.filter(is_success=False).count()
    notification_sent_count = notifications_health.filter(status="sent").count()
    notification_failed_count = notifications_health.filter(status="failed").count()
    total_connector = connector_success_count + connector_failure_count
    connector_success_rate_pct = round((connector_success_count / total_connector) * 100, 2) if total_connector else 100

    connector_failures_trend = list(
        connector_health.filter(is_success=False)
        .annotate(bucket=TruncHour("created_at"))
        .values("bucket")
        .annotate(count=Count("id"))
        .order_by("bucket")
    )

    return {
        "totals": totals,
        "refund_totals": refund_totals,
        "settlement_totals": settlement_totals,
        "dispute_counts": dispute_counts,
        "occupancy_totals": occupancy_totals,
        "total_units_sum": total_units_sum,
        "occupied_units_sum": occupied_units_sum,
        "total_capacity_sum": total_capacity_sum,
        "used_capacity_sum": used_capacity_sum,
        "occupancy_rate_pct": occupancy_rate_pct,
        "utilization_rate_pct": utilization_rate_pct,
        "stay_totals": stay_totals,
        "daily_revenue": daily_revenue,
        "top_tenants": top_tenants,
        "wallet_totals": wallet_totals,
        "withdrawal_requested_count": withdrawal_scope.filter(status="requested").count(),
        "withdrawal_approved_count": withdrawal_scope.filter(status="approved").count(),
        "withdrawal_paid_count": withdrawal_scope.filter(status="paid").count(),
        "marketplace_enabled_modules": marketplace_scope.count(),
        "marketplace_in_grace_modules": marketplace_scope.filter(commission_grace_until__gte=today).count(),
        "marketplace_commission_active_modules": marketplace_scope.filter(commission_grace_until__lt=today).count()
        + marketplace_scope.filter(commission_grace_until__isnull=True).count(),
        "health": {
            "connector_success_count": connector_success_count,
            "connector_failure_count": connector_failure_count,
            "connector_success_rate_pct": connector_success_rate_pct,
            "notification_sent_count": notification_sent_count,
            "notification_failed_count": notification_failed_count,
            "connector_failures_trend": [
                {"hour": row["bucket"].isoformat() if row["bucket"] else "", "count": row["count"] or 0}
                for row in connector_failures_trend
            ],
        },
    }
