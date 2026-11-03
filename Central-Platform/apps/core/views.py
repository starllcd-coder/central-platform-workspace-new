from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from apps.accounts.services import get_user_tenant_ids, user_has_permission
from apps.billing.models import DisputeCase, WalletAccount, WithdrawalRequest
from apps.pricing.models import TenantSubscription
from apps.tenants.models import Module, Tenant, TenantModule
from apps.tenants.policies import tenant_agreement_compliance_snapshot


def healthz(request):
    checks = {"database": False, "cache": False}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["database"] = True
    except Exception:
        pass

    try:
        cache.set("central:healthz", "ok", timeout=10)
        checks["cache"] = cache.get("central:healthz") == "ok"
    except Exception:
        pass

    healthy = all(checks.values())
    return JsonResponse(
        {"status": "ok" if healthy else "degraded", "checks": checks},
        status=200 if healthy else 503,
    )


@login_required
def dashboard(request):
    tenant_scope = Tenant.objects.all()
    if not request.user.is_superuser:
        tenant_scope = tenant_scope.filter(id__in=get_user_tenant_ids(request.user))

    scoped_tenant_ids = list(tenant_scope.values_list("id", flat=True))
    recent_tenants = list(tenant_scope.order_by("-created_at")[:8])
    compliance_rows = [tenant_agreement_compliance_snapshot(t) for t in recent_tenants]
    pending_any = [
        row
        for row in compliance_rows
        if not row["billing_ok"] or not row["marketplace_ok"]
    ]
    can_view_disputes = (
        request.user.is_superuser
        or user_has_permission(request.user, "reports.view")
        or user_has_permission(request.user, "billing.settle")
    )
    disputes_scope = DisputeCase.objects.all()
    if scoped_tenant_ids:
        disputes_scope = disputes_scope.filter(tenant_id__in=scoped_tenant_ids)
    elif not request.user.is_superuser:
        disputes_scope = DisputeCase.objects.none()

    marketplace_scope = TenantModule.objects.filter(enabled=True, marketplace_enabled=True)
    if scoped_tenant_ids:
        marketplace_scope = marketplace_scope.filter(tenant_id__in=scoped_tenant_ids)
    elif not request.user.is_superuser:
        marketplace_scope = TenantModule.objects.none()

    today = timezone.localdate()
    marketplace_in_grace = marketplace_scope.filter(commission_grace_until__gte=today).count()
    marketplace_commission_active = marketplace_scope.filter(
        commission_grace_until__lt=today
    ).count() + marketplace_scope.filter(commission_grace_until__isnull=True).count()
    wallet_scope = WalletAccount.objects.all()
    withdrawal_scope = WithdrawalRequest.objects.all()
    if not request.user.is_superuser:
        wallet_scope = wallet_scope.filter(tenant_id__in=scoped_tenant_ids)
        withdrawal_scope = withdrawal_scope.filter(tenant_id__in=scoped_tenant_ids)

    wallet_totals = wallet_scope.aggregate(
        available=Sum("available_balance"),
        pending=Sum("pending_balance"),
    )

    context = {
        "active_tenants": tenant_scope.filter(status="active").count(),
        "active_modules": TenantModule.objects.filter(
            enabled=True, tenant_id__in=scoped_tenant_ids
        ).count(),
        "marketplace_enabled_modules": marketplace_scope.count(),
        "marketplace_in_grace_modules": marketplace_in_grace,
        "marketplace_commission_active_modules": marketplace_commission_active,
        "wallet_available_total": wallet_totals.get("available") or 0,
        "wallet_pending_total": wallet_totals.get("pending") or 0,
        "withdrawal_requested_count": withdrawal_scope.filter(status="requested").count(),
        "withdrawal_approved_count": withdrawal_scope.filter(status="approved").count(),
        "withdrawal_paid_count": withdrawal_scope.filter(status="paid").count(),
        "subscriptions": TenantSubscription.objects.filter(
            status="active", tenant_id__in=scoped_tenant_ids
        ).count(),
        "modules_count": Module.objects.count(),
        "recent_tenants": recent_tenants[:5],
        "agreement_compliance_ok_count": len(compliance_rows) - len(pending_any),
        "agreement_compliance_pending_count": len(pending_any),
        "agreement_compliance_rows": pending_any[:6],
        "can_view_disputes": can_view_disputes,
        "dispute_counts": {
            "all": disputes_scope.count(),
            "pending": disputes_scope.filter(status__in=["open", "under_review"]).count(),
            "open": disputes_scope.filter(status="open").count(),
            "under_review": disputes_scope.filter(status="under_review").count(),
            "resolved": disputes_scope.filter(status="resolved").count(),
            "high_priority_pending": disputes_scope.filter(
                status__in=["open", "under_review"],
                opened_at__lte=timezone.now() - timedelta(hours=48),
            ).count(),
        },
    }
    return render(request, "core/dashboard.html", context)
