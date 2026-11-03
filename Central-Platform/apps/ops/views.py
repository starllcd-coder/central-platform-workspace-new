import csv

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from apps.accounts.permissions import require_permission
from apps.accounts.services import get_user_tenant_ids
from apps.billing.models import (
    DisputeCase,
    PaymentTransaction,
    RefundRecord,
    Settlement,
    WalletAccount,
    WithdrawalRequest,
)
from apps.tenants.models import TenantModule
from apps.tenants.models import Tenant
from apps.tenants.ranking import compute_marketplace_rankings
from apps.pricing.services import is_feature_enabled_for_tenant
from apps.stay.models import StayBooking

from .models import AuditLog, NotificationEvent, NotificationTemplate
from .models import OccupancySnapshot
from .analytics_service import build_analytics_snapshot
from .services import dispatch_notification


@login_required
@require_permission("reports.view")
def notifications_list(request):
    events = NotificationEvent.objects.select_related("tenant", "module", "template")
    module_id = _scoped_module_id(request)
    if module_id:
        events = events.filter(module_id=module_id)
    events = events[:100]
    templates = NotificationTemplate.objects.all()[:50]
    return render(
        request,
        "ops/notifications_list.html",
        {
            "events": events,
            "templates": templates,
        },
    )


@login_required
@require_permission("reports.view")
def audit_logs_list(request):
    logs = AuditLog.objects.select_related("actor", "tenant", "module")
    module_id = _scoped_module_id(request)
    if module_id:
        logs = logs.filter(module_id=module_id)
    logs = logs[:150]
    return render(
        request,
        "ops/audit_logs_list.html",
        {
            "logs": logs,
        },
    )


@login_required
@require_http_methods(["POST"])
@require_permission("connectors.manage")
def notification_retry(request, event_id):
    event = NotificationEvent.objects.filter(pk=event_id).first()
    if event:
        dispatch_notification(event)
    return redirect("ops-notifications-list")


def _scoped_tenant_ids(request):
    if request.user.is_superuser:
        return None
    return get_user_tenant_ids(request.user)


def _scoped_module_id(request):
    query_mid = request.GET.get("module_id")
    if query_mid and query_mid.isdigit():
        return int(query_mid)
    active_module = getattr(request, "active_module", None)
    return active_module.id if active_module else None


def _filter_date_range(qs, date_field, start, end):
    if start:
        qs = qs.filter(**{f"{date_field}__date__gte": start})
    if end:
        qs = qs.filter(**{f"{date_field}__date__lte": end})
    return qs


def _parse_date(value):
    if not value:
        return None
    try:
        return timezone.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _filter_date_range_datefield(qs, date_field, start, end):
    if start:
        qs = qs.filter(**{f"{date_field}__gte": start})
    if end:
        qs = qs.filter(**{f"{date_field}__lte": end})
    return qs


def _health_status_level(health):
    connector_failures = int(health.get("connector_failure_count") or 0)
    notification_failures = int(health.get("notification_failed_count") or 0)
    connector_success_rate = float(health.get("connector_success_rate_pct") or 0)
    if connector_failures >= 20 or notification_failures >= 10 or connector_success_rate < 90:
        return "critical"
    if connector_failures >= 5 or notification_failures >= 3 or connector_success_rate < 97:
        return "warning"
    return "healthy"


@login_required
@require_permission("reports.view")
def analytics_dashboard(request):
    return render(request, "ops/analytics.html")


@login_required
@require_permission("reports.view")
def marketplace_ranking_dashboard(request):
    module_id = _scoped_module_id(request)
    tenant_ids = _scoped_tenant_ids(request)
    rankings = compute_marketplace_rankings(
        module_id=module_id,
        tenant_ids=tenant_ids,
        limit=200,
    )
    return render(
        request,
        "ops/marketplace_ranking.html",
        {"rankings": rankings},
    )


@login_required
@require_permission("reports.view")
@require_GET
def marketplace_ranking_api(request):
    limit = request.GET.get("limit")
    limit = int(limit) if limit and limit.isdigit() else 100
    module_id = _scoped_module_id(request)
    tenant_ids = _scoped_tenant_ids(request)
    rankings = compute_marketplace_rankings(
        module_id=module_id,
        tenant_ids=tenant_ids,
        limit=limit,
    )
    return JsonResponse(
        {
            "results": [
                {
                    "rank": idx + 1,
                    "tenant_id": row["tenant_id"],
                    "tenant_code": row["tenant_code"],
                    "tenant_name": row["tenant_name"],
                    "module_id": row["module_id"],
                    "module_code": row["module_code"],
                    "module_name": row["module_name"],
                    "base_price": str(row["base_price"]),
                    "average_rating": str(row["average_rating"]),
                    "rating_count": row["rating_count"],
                    "plan_level_boost": str(row["plan_level_boost"]),
                    "manual_boost": str(row["manual_boost"]),
                    "score": str(row["score"]),
                }
                for idx, row in enumerate(rankings)
            ]
        }
    )


@login_required
@require_permission("reports.view")
@require_GET
def analytics_metrics_api(request):
    start = _parse_date(request.GET.get("start"))
    end = _parse_date(request.GET.get("end"))
    tenant_id = request.GET.get("tenant_id")
    tenant_id = int(tenant_id) if tenant_id and tenant_id.isdigit() else None
    module_id = _scoped_module_id(request)

    tenant_ids = _scoped_tenant_ids(request)
    if tenant_ids is not None:
        if tenant_id and tenant_id not in tenant_ids:
            return JsonResponse({"detail": "Tenant access denied."}, status=403)
    scoped_tenant_filter = tenant_ids if tenant_ids is not None else None

    snapshot = build_analytics_snapshot(
        tenant_id=tenant_id,
        scoped_tenant_filter=scoped_tenant_filter,
        module_id=module_id,
        start=start,
        end=end,
    )
    totals = snapshot["totals"]
    refund_totals = snapshot["refund_totals"]
    settlement_totals = snapshot["settlement_totals"]
    dispute_counts = snapshot["dispute_counts"]
    wallet_totals = snapshot["wallet_totals"]
    stay_totals = snapshot["stay_totals"]
    daily_revenue = snapshot["daily_revenue"]
    top_tenants = snapshot["top_tenants"]

    return JsonResponse(
        {
            "totals": {
                "gross": str(totals.get("gross") or 0),
                "commission": str(totals.get("commission") or 0),
                "net": str(totals.get("net") or 0),
                "tx_count": totals.get("tx_count") or 0,
                "refund_amount": str(refund_totals.get("refund_amount") or 0),
                "refund_count": refund_totals.get("refund_count") or 0,
                "payout_total": str(settlement_totals.get("payout_total") or 0),
                "settlement_count": settlement_totals.get("settlement_count") or 0,
                "marketplace_enabled_modules": snapshot["marketplace_enabled_modules"],
                "marketplace_in_grace_modules": snapshot["marketplace_in_grace_modules"],
                "marketplace_commission_active_modules": snapshot["marketplace_commission_active_modules"],
                "wallet_available_total": str(wallet_totals.get("wallet_available_total") or 0),
                "wallet_pending_total": str(wallet_totals.get("wallet_pending_total") or 0),
                "withdrawal_requested_count": snapshot["withdrawal_requested_count"],
                "withdrawal_approved_count": snapshot["withdrawal_approved_count"],
                "withdrawal_paid_count": snapshot["withdrawal_paid_count"],
                "occupancy_total_units": snapshot["total_units_sum"],
                "occupancy_occupied_units": snapshot["occupied_units_sum"],
                "occupancy_rate_pct": snapshot["occupancy_rate_pct"],
                "utilization_total_capacity": snapshot["total_capacity_sum"],
                "utilization_used_capacity": snapshot["used_capacity_sum"],
                "utilization_rate_pct": snapshot["utilization_rate_pct"],
                "occupancy_snapshot_days": snapshot["occupancy_totals"].get("snapshot_days") or 0,
                "stay_revenue_total": str(stay_totals.get("stay_revenue_total") or 0),
                "stay_original_revenue": str(stay_totals.get("stay_original_revenue") or 0),
                "stay_extension_revenue": str(stay_totals.get("stay_extension_revenue") or 0),
                "stay_extension_count": stay_totals.get("stay_extension_count") or 0,
            },
            "disputes": dispute_counts,
            "daily_revenue": [
                {
                    "date": row["occurred_at__date"].isoformat(),
                    "gross": str(row["gross"] or 0),
                    "commission": str(row["commission"] or 0),
                    "net": str(row["net"] or 0),
                }
                for row in daily_revenue
            ],
            "top_tenants": [
                {
                    "tenant_name": row["tenant__name"] or "Unknown",
                    "gross": str(row["gross"] or 0),
                    "tx_count": row["tx_count"] or 0,
                }
                for row in top_tenants
            ],
            "health": snapshot.get("health", {}),
        }
    )


@login_required
@require_permission("reports.view")
@require_GET
def health_summary_api(request):
    tenant_id = request.GET.get("tenant_id")
    tenant_id = int(tenant_id) if tenant_id and tenant_id.isdigit() else None
    module_id = _scoped_module_id(request)

    tenant_ids = _scoped_tenant_ids(request)
    if tenant_ids is not None and tenant_id and tenant_id not in tenant_ids:
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    scoped_tenant_filter = tenant_ids if tenant_ids is not None else None

    snapshot = build_analytics_snapshot(
        tenant_id=tenant_id,
        scoped_tenant_filter=scoped_tenant_filter,
        module_id=module_id,
        start=None,
        end=None,
    )
    health = snapshot.get("health", {})
    level = _health_status_level(health)
    return JsonResponse(
        {
            "status": level,
            "health": health,
            "thresholds": {
                "critical_connector_failures": 20,
                "critical_notification_failures": 10,
                "critical_connector_success_rate_pct": 90,
            },
        }
    )


@login_required
@require_permission("reports.view")
@require_GET
def analytics_export_csv(request):
    start = _parse_date(request.GET.get("start"))
    end = _parse_date(request.GET.get("end"))
    tenant_id = request.GET.get("tenant_id")
    tenant_id = int(tenant_id) if tenant_id and tenant_id.isdigit() else None
    module_id = _scoped_module_id(request)

    tenant_ids = _scoped_tenant_ids(request)
    if tenant_ids is not None:
        if tenant_id and tenant_id not in tenant_ids:
            return JsonResponse({"detail": "Tenant access denied."}, status=403)
    scoped_tenant_filter = tenant_ids if tenant_ids is not None else None

    feature_code = "analytics.export_csv"
    gated_tenant = None
    if tenant_id:
        gated_tenant = Tenant.objects.filter(pk=tenant_id).first()
    elif getattr(request, "active_tenant", None):
        gated_tenant = getattr(request, "active_tenant", None)

    if gated_tenant is not None:
        if not is_feature_enabled_for_tenant(
            tenant=gated_tenant,
            feature_code=feature_code,
            default_if_missing=True,
        ):
            return JsonResponse(
                {"detail": "Feature not enabled for tenant: analytics_export_csv."},
                status=403,
            )
    elif scoped_tenant_filter is not None:
        any_enabled = False
        for tenant in Tenant.objects.filter(id__in=scoped_tenant_filter)[:200]:
            if is_feature_enabled_for_tenant(
                tenant=tenant,
                feature_code=feature_code,
                default_if_missing=True,
            ):
                any_enabled = True
                break
        if not any_enabled:
            return JsonResponse(
                {"detail": "Feature not enabled for your tenant scope: analytics_export_csv."},
                status=403,
            )

    snapshot = build_analytics_snapshot(
        tenant_id=tenant_id,
        scoped_tenant_filter=scoped_tenant_filter,
        module_id=module_id,
        start=start,
        end=end,
    )
    totals = snapshot["totals"]
    refund_totals = snapshot["refund_totals"]
    settlement_totals = snapshot["settlement_totals"]
    dispute_counts = snapshot["dispute_counts"]
    wallet_totals = snapshot["wallet_totals"]
    stay_totals = snapshot["stay_totals"]
    daily_revenue = snapshot["daily_revenue"]
    top_tenants = snapshot["top_tenants"]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="analytics_export.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "row_type",
            "date",
            "tenant_name",
            "status",
            "gross",
            "commission",
            "net",
            "tx_count",
            "refund_amount",
            "refund_count",
            "payout_total",
            "settlement_count",
            "count",
            "marketplace_enabled_modules",
            "marketplace_in_grace_modules",
            "marketplace_commission_active_modules",
            "wallet_available_total",
            "wallet_pending_total",
            "withdrawal_requested_count",
            "withdrawal_approved_count",
            "withdrawal_paid_count",
            "occupancy_total_units",
            "occupancy_occupied_units",
            "occupancy_rate_pct",
            "utilization_total_capacity",
            "utilization_used_capacity",
            "utilization_rate_pct",
            "occupancy_snapshot_days",
            "stay_revenue_total",
            "stay_original_revenue",
            "stay_extension_revenue",
            "stay_extension_count",
        ]
    )
    writer.writerow(
        [
            "totals",
            "",
            "",
            "",
            str(totals.get("gross") or 0),
            str(totals.get("commission") or 0),
            str(totals.get("net") or 0),
            totals.get("tx_count") or 0,
            str(refund_totals.get("refund_amount") or 0),
            refund_totals.get("refund_count") or 0,
            str(settlement_totals.get("payout_total") or 0),
            settlement_totals.get("settlement_count") or 0,
            "",
            snapshot["marketplace_enabled_modules"],
            snapshot["marketplace_in_grace_modules"],
            snapshot["marketplace_commission_active_modules"],
            str(wallet_totals.get("wallet_available_total") or 0),
            str(wallet_totals.get("wallet_pending_total") or 0),
            snapshot["withdrawal_requested_count"],
            snapshot["withdrawal_approved_count"],
            snapshot["withdrawal_paid_count"],
            snapshot["total_units_sum"],
            snapshot["occupied_units_sum"],
            snapshot["occupancy_rate_pct"],
            snapshot["total_capacity_sum"],
            snapshot["used_capacity_sum"],
            snapshot["utilization_rate_pct"],
            snapshot["occupancy_totals"].get("snapshot_days") or 0,
            str(stay_totals.get("stay_revenue_total") or 0),
            str(stay_totals.get("stay_original_revenue") or 0),
            str(stay_totals.get("stay_extension_revenue") or 0),
            stay_totals.get("stay_extension_count") or 0,
        ]
    )
    for row in dispute_counts:
        writer.writerow(
            [
                "dispute_status",
                "",
                "",
                row["status"],
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                row["count"] or 0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )
    for row in top_tenants:
        writer.writerow(
            [
                "top_tenant",
                "",
                row["tenant__name"] or "Unknown",
                "",
                str(row["gross"] or 0),
                "",
                "",
                row["tx_count"] or 0,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )
    for row in daily_revenue:
        writer.writerow(
            [
                "daily_revenue",
                row["occurred_at__date"].isoformat(),
                "",
                "",
                str(row["gross"] or 0),
                str(row["commission"] or 0),
                str(row["net"] or 0),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )
    return response
