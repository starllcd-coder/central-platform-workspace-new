from datetime import date

from django.conf import settings
from django.db import models
from django.utils import timezone

from .models import AgreementDocument, TenantAgreementAcceptance

REQUIRED_AGREEMENTS = {
    "billing": ["TOS", "PAYMENT"],
    "marketplace": ["TOS", "COMMISSION", "PAYMENT"],
}


def latest_active_documents_by_code(codes):
    today = timezone.localdate()
    docs = (
        AgreementDocument.objects.filter(
            is_active=True,
            code__in=codes,
            effective_from__lte=today,
        )
        .order_by("code", "-effective_from", "-created_at")
    )
    by_code = {}
    for doc in docs:
        if doc.code not in by_code:
            by_code[doc.code] = doc
    return by_code


def tenant_missing_required_codes(tenant, codes):
    docs_by_code = latest_active_documents_by_code(codes)
    doc_ids = [d.id for d in docs_by_code.values()]
    accepted_ids = set(
        TenantAgreementAcceptance.objects.filter(
            tenant=tenant,
            document_id__in=doc_ids,
        ).values_list("document_id", flat=True)
    )
    missing = []
    for code in codes:
        doc = docs_by_code.get(code)
        if doc is None:
            # If no active version exists, treat as required configuration gap.
            missing.append(code)
        elif doc.id not in accepted_ids:
            missing.append(code)
    return missing


def tenant_missing_required_policy(tenant, policy_name):
    return tenant_missing_required_codes(tenant, REQUIRED_AGREEMENTS.get(policy_name, []))


def tenant_agreement_compliance_snapshot(tenant):
    billing_missing = tenant_missing_required_policy(tenant, "billing")
    marketplace_missing = tenant_missing_required_policy(tenant, "marketplace")
    return {
        "tenant": tenant,
        "billing_missing": billing_missing,
        "marketplace_missing": marketplace_missing,
        "billing_ok": len(billing_missing) == 0,
        "marketplace_ok": len(marketplace_missing) == 0,
    }


def pricing_subscription_cutoff_date():
    configured = getattr(settings, "PRICING_SUBSCRIPTION_CUTOFF_DATE", None)
    if isinstance(configured, date):
        return configured
    return date(2026, 1, 1)


def _tenant_onboarding_date(tenant):
    return tenant.onboarding_date or timezone.localdate(tenant.created_at)


def _pricing_version_number(pricing_version):
    if not pricing_version:
        return None
    text = str(pricing_version).strip().lower()
    if text.startswith("v") and text[1:].isdigit():
        return int(text[1:])
    return None


def tenant_is_new_pricing_customer(tenant):
    return _tenant_onboarding_date(tenant) >= pricing_subscription_cutoff_date()


def tenant_demo_block_reason(tenant):
    if getattr(tenant, "account_type", "production") != "demo":
        return ""

    if tenant.demo_expires_on and tenant.demo_expires_on < timezone.localdate():
        return (
            f"Demo tenant expired on {tenant.demo_expires_on.isoformat()}. "
            "Convert it to a paid account before enabling live operations."
        )

    expiry_text = tenant.demo_expires_on.isoformat() if tenant.demo_expires_on else "its configured expiry date"
    return (
        f"Tenant {tenant.tenant_code} is a demo sandbox until {expiry_text}. "
        "Billing, payment processing, and external connector traffic are disabled for demo tenants."
    )


def tenant_grandfathering_errors(tenant):
    errors = []
    is_new = tenant_is_new_pricing_customer(tenant)
    version_num = _pricing_version_number(tenant.pricing_version)

    if is_new and tenant.pricing_model != "subscription":
        errors.append(
            "New tenants (on or after cutoff date) must use subscription pricing model."
        )
    if is_new and (version_num is None or version_num < 2):
        errors.append(
            "New tenants must be assigned pricing_version v2 or higher."
        )

    return errors


def current_subscription_status_for_tenant(tenant):
    today = timezone.localdate()
    active_like = tenant.subscriptions.filter(
        status__in=["active", "trial"],
        start_date__lte=today,
    ).filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=today))
    ordered = active_like.order_by(
        models.Case(
            models.When(status="active", then=0),
            models.When(status="trial", then=1),
            default=2,
            output_field=models.IntegerField(),
        ),
        "-start_date",
        "-id",
    )
    row = ordered.first()
    if row:
        return row.status
    return "inactive"


def sync_tenant_subscription_status(tenant):
    if tenant.pricing_model not in {"subscription", "hybrid"}:
        return tenant.subscription_status

    expected = current_subscription_status_for_tenant(tenant)
    if tenant.subscription_status != expected:
        tenant.subscription_status = expected
        tenant.save(update_fields=["subscription_status", "updated_at"])
    return expected


def tenant_billing_block_reason(tenant):
    demo_issue = tenant_demo_block_reason(tenant)
    if demo_issue:
        return demo_issue

    issues = tenant_grandfathering_errors(tenant)
    if issues:
        return " ".join(issues)

    if tenant.pricing_model in {"one_time", "hybrid"} and not tenant.onboarding_fee_paid:
        return (
            "Onboarding fee is not marked as paid for this tenant. "
            "Set onboarding_fee_paid=true before posting billing transactions."
        )

    subscription_status = sync_tenant_subscription_status(tenant)
    if tenant.pricing_model in {"subscription", "hybrid"} and subscription_status not in {
        "trial",
        "active",
    }:
        return (
            "Tenant subscription is not active. Set subscription_status to trial or active "
            "before posting billing transactions."
        )
    return ""
