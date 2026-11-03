from django.db import models
from django.db import transaction
from django.utils import timezone

from apps.tenants.models import Tenant
from apps.tenants.policies import sync_tenant_subscription_status

from .models import (
    AddOnFeatureEntitlement,
    Feature,
    PlanFeatureEntitlement,
    PricingTransition,
    TenantAddOnSubscription,
    TenantFeatureOverride,
    TenantSubscription,
)


def _active_subscription_for_tenant(tenant: Tenant, on_date=None):
    day = on_date or timezone.localdate()
    qs = TenantSubscription.objects.filter(
        tenant=tenant,
        status__in=["active", "trial"],
        start_date__lte=day,
    ).filter(
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=day)
    )
    return qs.order_by("-start_date", "-id").first()


def _active_override(tenant: Tenant, feature: Feature, on_date=None):
    day = on_date or timezone.localdate()
    qs = TenantFeatureOverride.objects.filter(tenant=tenant, feature=feature)
    qs = qs.filter(
        models.Q(starts_on__isnull=True) | models.Q(starts_on__lte=day)
    ).filter(
        models.Q(ends_on__isnull=True) | models.Q(ends_on__gte=day)
    )
    return qs.order_by("-updated_at", "-id").first()


def _active_add_on_subscriptions_for_tenant(tenant: Tenant, on_date=None):
    day = on_date or timezone.localdate()
    qs = TenantAddOnSubscription.objects.select_related("add_on").filter(
        tenant=tenant,
        status__in=["active", "trial"],
        start_date__lte=day,
    )
    qs = qs.filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=day))
    return qs.order_by("-start_date", "-id")


def resolve_feature_for_tenant(tenant: Tenant, feature_code: str, on_date=None, default_if_missing=True):
    feature = Feature.objects.filter(code=feature_code, is_active=True).first()
    if feature is None:
        return {
            "feature_code": feature_code,
            "enabled": bool(default_if_missing),
            "source": "missing_feature_default",
        }

    override = _active_override(tenant=tenant, feature=feature, on_date=on_date)
    if override is not None:
        return {
            "feature_code": feature_code,
            "enabled": bool(override.enabled),
            "source": "tenant_override",
        }

    sub = _active_subscription_for_tenant(tenant=tenant, on_date=on_date)
    if sub is not None:
        entitlement = PlanFeatureEntitlement.objects.filter(
            plan_version=sub.plan_version,
            feature=feature,
        ).first()
        if entitlement is not None:
            return {
                "feature_code": feature_code,
                "enabled": bool(entitlement.enabled),
                "source": "plan_entitlement",
            }

    active_add_ons = _active_add_on_subscriptions_for_tenant(tenant=tenant, on_date=on_date)
    add_on_ids = [row.add_on_id for row in active_add_ons]
    if add_on_ids:
        add_on_entitlement = AddOnFeatureEntitlement.objects.filter(
            add_on_id__in=add_on_ids,
            feature=feature,
            enabled=True,
        ).first()
        if add_on_entitlement is not None:
            return {
                "feature_code": feature_code,
                "enabled": True,
                "source": "addon_entitlement",
            }

    return {
        "feature_code": feature_code,
        "enabled": bool(feature.default_enabled),
        "source": "feature_default",
    }


def is_feature_enabled_for_tenant(tenant: Tenant, feature_code: str, on_date=None, default_if_missing=True):
    resolved = resolve_feature_for_tenant(
        tenant=tenant,
        feature_code=feature_code,
        on_date=on_date,
        default_if_missing=default_if_missing,
    )
    return bool(resolved["enabled"])


def schedule_pricing_transition(
    *,
    tenant: Tenant,
    target_plan_version,
    effective_on,
    created_by=None,
    notes="",
):
    duplicate = PricingTransition.objects.filter(
        tenant=tenant,
        target_plan_version=target_plan_version,
        effective_on=effective_on,
        status="scheduled",
    ).first()
    if duplicate:
        return duplicate, False

    row = PricingTransition.objects.create(
        tenant=tenant,
        target_plan_version=target_plan_version,
        effective_on=effective_on,
        status="scheduled",
        created_by=created_by,
        notes=notes or "",
    )
    return row, True


@transaction.atomic
def apply_pricing_transition(transition: PricingTransition, *, actor=None, run_date=None):
    if transition.status != "scheduled":
        raise ValueError("Only scheduled transitions can be applied.")

    today = run_date or timezone.localdate()
    if today < transition.effective_on:
        raise ValueError("Transition effective date has not been reached.")

    tenant = transition.tenant
    target = transition.target_plan_version

    source = (
        TenantSubscription.objects.filter(
            tenant=tenant,
            status__in=["active", "trial"],
            start_date__lte=transition.effective_on,
        )
        .filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=transition.effective_on))
        .order_by("-start_date", "-id")
        .first()
    )

    if source and source.plan_version_id == target.id and source.start_date == transition.effective_on:
        applied_subscription = source
    else:
        if source:
            source.end_date = transition.effective_on
            source.status = "cancelled"
            source.save(update_fields=["end_date", "status"])

        applied_subscription = TenantSubscription.objects.create(
            tenant=tenant,
            plan_version=target,
            status="active",
            start_date=transition.effective_on,
            end_date=None,
            pricing_version=target.version,
        )

    tenant.pricing_model = target.plan.billing_type
    tenant.pricing_version = target.version
    tenant.subscription_status = "active"
    tenant.save(update_fields=["pricing_model", "pricing_version", "subscription_status", "updated_at"])
    sync_tenant_subscription_status(tenant)

    transition.source_subscription = source
    transition.applied_subscription = applied_subscription
    transition.status = "applied"
    transition.applied_by = actor
    transition.applied_at = timezone.now()
    transition.failure_reason = ""
    transition.save(
        update_fields=[
            "source_subscription",
            "applied_subscription",
            "status",
            "applied_by",
            "applied_at",
            "failure_reason",
            "updated_at",
        ]
    )
    return transition


def apply_due_pricing_transitions(*, run_date=None, limit=100):
    day = run_date or timezone.localdate()
    rows = (
        PricingTransition.objects.select_related("tenant", "target_plan_version__plan")
        .filter(status="scheduled", effective_on__lte=day)
        .order_by("effective_on", "id")[: max(1, int(limit))]
    )
    applied_count = 0
    failed_count = 0
    for row in rows:
        try:
            apply_pricing_transition(row, actor=None, run_date=day)
            applied_count += 1
        except Exception as exc:
            row.status = "failed"
            row.failure_reason = str(exc)[:255]
            row.save(update_fields=["status", "failure_reason", "updated_at"])
            failed_count += 1
    return {
        "considered": len(rows),
        "applied": applied_count,
        "failed": failed_count,
    }
