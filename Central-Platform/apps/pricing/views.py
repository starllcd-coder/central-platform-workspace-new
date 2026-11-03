import json
from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.accounts.permissions import require_permission
from apps.accounts.services import get_user_tenant_ids, user_can_access_tenant, user_has_permission
from apps.tenants.models import Module, Tenant
from apps.ops.services import log_audit

from .forms import AddOnForm, CommissionRuleForm, PricingTransitionForm, TenantAddOnSubscriptionForm
from .models import AddOn, CommissionRule, PlanVersion, PricingTransition, TenantAddOnSubscription
from .services import apply_pricing_transition, resolve_feature_for_tenant, schedule_pricing_transition


@login_required
def pricing_list(request):
    versions = PlanVersion.objects.select_related("plan").order_by("plan__name", "version")
    rules = CommissionRule.objects.select_related("tenant", "module").all()
    add_ons = AddOn.objects.all()
    tenant_add_ons = TenantAddOnSubscription.objects.select_related("tenant", "add_on")
    transitions = PricingTransition.objects.select_related(
        "tenant",
        "target_plan_version__plan",
        "source_subscription",
        "applied_subscription",
        "created_by",
        "applied_by",
    )
    if not request.user.is_superuser:
        tenant_ids = get_user_tenant_ids(request.user)
        rules = rules.filter(models.Q(tenant_id__in=tenant_ids) | models.Q(tenant__isnull=True))
        tenant_add_ons = tenant_add_ons.filter(tenant_id__in=tenant_ids)
        transitions = transitions.filter(tenant_id__in=tenant_ids)
    rules = rules[:50]
    add_ons = add_ons[:100]
    tenant_add_ons = tenant_add_ons.order_by("-start_date", "-id")[:100]
    transitions = transitions.order_by("status", "effective_on", "-created_at")[:100]
    return render(
        request,
        "pricing/list.html",
        {
            "versions": versions,
            "rules": rules,
            "add_ons": add_ons,
            "tenant_add_ons": tenant_add_ons,
            "add_on_form": AddOnForm(),
            "tenant_add_on_form": TenantAddOnSubscriptionForm(),
            "transitions": transitions,
            "transition_form": PricingTransitionForm(),
        },
    )


@login_required
@require_permission("commission.manage")
def commission_rule_create(request):
    if request.method == "POST":
        form = CommissionRuleForm(request.POST)
        if form.is_valid():
            rule = form.save()
            log_audit(
                actor=request.user,
                tenant=rule.tenant,
                module=rule.module,
                action="pricing.commission_rule.created",
                entity_type="CommissionRule",
                entity_id=rule.id,
                metadata={"rate_percent": str(rule.rate_percent), "booking_type": rule.booking_type},
            )
            messages.success(request, "Commission rule created.")
            return redirect("pricing-list")
    else:
        form = CommissionRuleForm()

    return render(
        request,
        "pricing/commission_form.html",
        {
            "form": form,
            "title": "Create Commission Rule",
            "submit_label": "Create Rule",
        },
    )


@login_required
@require_permission("commission.manage")
def commission_rule_edit(request, rule_id):
    rule = get_object_or_404(CommissionRule, pk=rule_id)
    if rule.tenant_id and not user_can_access_tenant(request.user, rule.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    if request.method == "POST":
        form = CommissionRuleForm(request.POST, instance=rule)
        if form.is_valid():
            rule = form.save()
            log_audit(
                actor=request.user,
                tenant=rule.tenant,
                module=rule.module,
                action="pricing.commission_rule.updated",
                entity_type="CommissionRule",
                entity_id=rule.id,
                metadata={"rate_percent": str(rule.rate_percent), "booking_type": rule.booking_type},
            )
            messages.success(request, "Commission rule updated.")
            return redirect("pricing-list")
    else:
        form = CommissionRuleForm(instance=rule)

    return render(
        request,
        "pricing/commission_form.html",
        {
            "form": form,
            "title": "Edit Commission Rule",
            "submit_label": "Save Changes",
            "rule": rule,
        },
    )


@login_required
@require_http_methods(["POST"])
@require_permission("commission.manage")
def commission_rule_toggle(request, rule_id):
    rule = get_object_or_404(CommissionRule, pk=rule_id)
    if rule.tenant_id and not user_can_access_tenant(request.user, rule.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    rule.is_active = not rule.is_active
    rule.save(update_fields=["is_active", "updated_at"])
    log_audit(
        actor=request.user,
        tenant=rule.tenant,
        module=rule.module,
        action="pricing.commission_rule.toggled",
        entity_type="CommissionRule",
        entity_id=rule.id,
        metadata={"is_active": rule.is_active},
    )
    messages.success(
        request,
        f"Commission rule {'activated' if rule.is_active else 'deactivated'}.",
    )
    return redirect("pricing-list")


def _staff_guard(user):
    return user_has_permission(user, "commission.manage")


def _rule_to_dict(rule):
    return {
        "id": rule.id,
        "tenant_id": rule.tenant_id,
        "tenant_code": rule.tenant.tenant_code if rule.tenant else None,
        "module_id": rule.module_id,
        "module_code": rule.module.code if rule.module else None,
        "booking_type": rule.booking_type,
        "rate_percent": str(rule.rate_percent),
        "fixed_fee": str(rule.fixed_fee),
        "effective_from": rule.effective_from.isoformat(),
        "effective_to": rule.effective_to.isoformat() if rule.effective_to else None,
        "is_active": rule.is_active,
        "notes": rule.notes,
    }


def _parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}, expected YYYY-MM-DD")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def commission_rules_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)

    if request.method == "GET":
        qs = CommissionRule.objects.select_related("tenant", "module").all()
        tenant_id = request.GET.get("tenant_id")
        module_code = request.GET.get("module_code")
        is_active = request.GET.get("is_active")

        if tenant_id and tenant_id.isdigit():
            qs = qs.filter(tenant_id=int(tenant_id))
        if module_code:
            qs = qs.filter(module__code=module_code)
        if is_active in {"true", "false"}:
            qs = qs.filter(is_active=(is_active == "true"))
        if not request.user.is_superuser:
            tenant_ids = get_user_tenant_ids(request.user)
            qs = qs.filter(models.Q(tenant_id__in=tenant_ids) | models.Q(tenant__isnull=True))

        return JsonResponse({"results": [_rule_to_dict(rule) for rule in qs[:200]]})

    if not _staff_guard(request.user):
        return JsonResponse({"detail": "Staff access required."}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    try:
        tenant = None
        if payload.get("tenant_id") is not None:
            tenant = Tenant.objects.get(pk=payload["tenant_id"])
            if not user_can_access_tenant(request.user, tenant.id):
                return JsonResponse({"detail": "Tenant access denied."}, status=403)

        module = None
        if payload.get("module_id") is not None:
            module = Module.objects.get(pk=payload["module_id"])

        booking_type = payload.get("booking_type", "all")
        if booking_type not in {"all", "online", "cash"}:
            raise ValueError("booking_type must be one of: all, online, cash")

        rate_percent = Decimal(str(payload.get("rate_percent", "")))
        fixed_fee = Decimal(str(payload.get("fixed_fee", "0")))
        effective_from = _parse_date(payload.get("effective_from"), "effective_from")
        effective_to_value = payload.get("effective_to")
        effective_to = _parse_date(effective_to_value, "effective_to") if effective_to_value else None

        rule = CommissionRule.objects.create(
            tenant=tenant,
            module=module,
            booking_type=booking_type,
            rate_percent=rate_percent,
            fixed_fee=fixed_fee,
            effective_from=effective_from,
            effective_to=effective_to,
            is_active=payload.get("is_active", True),
            notes=payload.get("notes", ""),
        )
    except Tenant.DoesNotExist:
        return JsonResponse({"detail": "tenant_id not found."}, status=404)
    except Module.DoesNotExist:
        return JsonResponse({"detail": "module_id not found."}, status=404)
    except ValidationError as exc:
        message = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        return JsonResponse({"detail": message}, status=400)
    except InvalidOperation:
        return JsonResponse({"detail": "rate_percent/fixed_fee must be numeric."}, status=400)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(_rule_to_dict(rule), status=201)


@csrf_exempt
@require_http_methods(["PATCH", "POST"])
def commission_rule_status_api(request, rule_id):
    if not _staff_guard(request.user):
        return JsonResponse({"detail": "Staff access required."}, status=403)

    try:
        rule = CommissionRule.objects.get(pk=rule_id)
    except CommissionRule.DoesNotExist:
        return JsonResponse({"detail": "Rule not found."}, status=404)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    is_active = payload.get("is_active")
    if not isinstance(is_active, bool):
        return JsonResponse({"detail": "is_active boolean is required."}, status=400)
    if rule.tenant_id and not user_can_access_tenant(request.user, rule.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)

    rule.is_active = is_active
    try:
        rule.save(update_fields=["is_active", "updated_at"])
    except ValidationError as exc:
        message = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        return JsonResponse({"detail": message}, status=400)
    return JsonResponse(_rule_to_dict(rule))


@require_http_methods(["GET"])
def feature_check_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)

    feature_code = (request.GET.get("feature_code") or "").strip()
    tenant_id = request.GET.get("tenant_id")
    if not feature_code:
        return JsonResponse({"detail": "feature_code is required."}, status=400)
    if not tenant_id or not tenant_id.isdigit():
        return JsonResponse({"detail": "tenant_id is required."}, status=400)

    tenant = Tenant.objects.filter(pk=int(tenant_id)).first()
    if tenant is None:
        return JsonResponse({"detail": "tenant_id not found."}, status=404)
    if not user_can_access_tenant(request.user, tenant.id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)

    resolved = resolve_feature_for_tenant(
        tenant=tenant,
        feature_code=feature_code,
        default_if_missing=True,
    )
    return JsonResponse(
        {
            "tenant_id": tenant.id,
            "tenant_code": tenant.tenant_code,
            "feature_code": feature_code,
            "enabled": bool(resolved["enabled"]),
            "source": resolved["source"],
        }
    )


@login_required
@require_http_methods(["POST"])
@require_permission("commission.manage")
def add_on_create(request):
    form = AddOnForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Add-on form is invalid.")
        return redirect("pricing-list")
    add_on = form.save()
    log_audit(
        actor=request.user,
        tenant=None,
        action="pricing.addon.created",
        entity_type="AddOn",
        entity_id=add_on.id,
        metadata={"code": add_on.code, "price": str(add_on.price), "billing_cycle": add_on.billing_cycle},
    )
    messages.success(request, "Add-on created.")
    return redirect("pricing-list")


@login_required
@require_http_methods(["POST"])
@require_permission("commission.manage")
def tenant_add_on_subscribe(request):
    form = TenantAddOnSubscriptionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Tenant add-on subscription form is invalid.")
        return redirect("pricing-list")

    row = form.save(commit=False)
    if not user_can_access_tenant(request.user, row.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    row.save()
    log_audit(
        actor=request.user,
        tenant=row.tenant,
        action="pricing.addon.subscription.created",
        entity_type="TenantAddOnSubscription",
        entity_id=row.id,
        metadata={"add_on_id": row.add_on_id, "status": row.status, "start_date": row.start_date.isoformat()},
    )
    messages.success(request, "Tenant add-on subscription created.")
    return redirect("pricing-list")


def _add_on_to_dict(add_on):
    return {
        "id": add_on.id,
        "code": add_on.code,
        "name": add_on.name,
        "description": add_on.description,
        "billing_cycle": add_on.billing_cycle,
        "price": str(add_on.price),
        "is_active": add_on.is_active,
    }


def _tenant_add_on_to_dict(row):
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "tenant_code": row.tenant.tenant_code if row.tenant else None,
        "add_on_id": row.add_on_id,
        "add_on_code": row.add_on.code if row.add_on else None,
        "status": row.status,
        "start_date": row.start_date.isoformat(),
        "end_date": row.end_date.isoformat() if row.end_date else None,
        "notes": row.notes,
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def add_ons_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)

    if request.method == "GET":
        qs = AddOn.objects.all()
        is_active = request.GET.get("is_active")
        if is_active in {"true", "false"}:
            qs = qs.filter(is_active=(is_active == "true"))
        return JsonResponse({"results": [_add_on_to_dict(row) for row in qs[:200]]})

    if not _staff_guard(request.user):
        return JsonResponse({"detail": "Staff access required."}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    billing_cycle = payload.get("billing_cycle", "monthly")
    if billing_cycle not in {"monthly", "yearly", "one_time"}:
        return JsonResponse({"detail": "billing_cycle must be monthly/yearly/one_time."}, status=400)
    try:
        price = Decimal(str(payload.get("price", "0")))
    except InvalidOperation:
        return JsonResponse({"detail": "price must be numeric."}, status=400)
    code = str(payload.get("code", "")).strip()
    name = str(payload.get("name", "")).strip()
    if not code or not name:
        return JsonResponse({"detail": "code and name are required."}, status=400)

    add_on = AddOn.objects.create(
        code=code,
        name=name,
        description=str(payload.get("description", "")),
        billing_cycle=billing_cycle,
        price=price,
        is_active=bool(payload.get("is_active", True)),
    )
    return JsonResponse(_add_on_to_dict(add_on), status=201)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def tenant_add_ons_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)

    if request.method == "GET":
        qs = TenantAddOnSubscription.objects.select_related("tenant", "add_on")
        tenant_id = request.GET.get("tenant_id")
        status = request.GET.get("status")
        if tenant_id and tenant_id.isdigit():
            qs = qs.filter(tenant_id=int(tenant_id))
        if status in {"active", "trial", "cancelled"}:
            qs = qs.filter(status=status)
        if not request.user.is_superuser:
            qs = qs.filter(tenant_id__in=get_user_tenant_ids(request.user))
        return JsonResponse({"results": [_tenant_add_on_to_dict(row) for row in qs[:200]]})

    if not _staff_guard(request.user):
        return JsonResponse({"detail": "Staff access required."}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    tenant_id = payload.get("tenant_id")
    add_on_id = payload.get("add_on_id")
    if not isinstance(tenant_id, int) or not isinstance(add_on_id, int):
        return JsonResponse({"detail": "tenant_id and add_on_id are required integers."}, status=400)
    tenant = Tenant.objects.filter(pk=tenant_id).first()
    if tenant is None:
        return JsonResponse({"detail": "tenant_id not found."}, status=404)
    if not user_can_access_tenant(request.user, tenant.id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    add_on = AddOn.objects.filter(pk=add_on_id).first()
    if add_on is None:
        return JsonResponse({"detail": "add_on_id not found."}, status=404)
    status = payload.get("status", "active")
    if status not in {"active", "trial", "cancelled"}:
        return JsonResponse({"detail": "status must be active/trial/cancelled."}, status=400)
    try:
        start_date = _parse_date(payload.get("start_date"), "start_date")
        end_date_value = payload.get("end_date")
        end_date = _parse_date(end_date_value, "end_date") if end_date_value else None
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    row = TenantAddOnSubscription.objects.create(
        tenant=tenant,
        add_on=add_on,
        status=status,
        start_date=start_date,
        end_date=end_date,
        notes=str(payload.get("notes", "")),
    )
    return JsonResponse(_tenant_add_on_to_dict(row), status=201)


@login_required
@require_http_methods(["POST"])
@require_permission("commission.manage")
def pricing_transition_create(request):
    form = PricingTransitionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Transition form is invalid.")
        return redirect("pricing-list")

    tenant = form.cleaned_data["tenant"]
    if not user_can_access_tenant(request.user, tenant.id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    target_plan_version = form.cleaned_data["target_plan_version"]
    effective_on = form.cleaned_data["effective_on"]
    notes = form.cleaned_data.get("notes", "")

    transition, created = schedule_pricing_transition(
        tenant=tenant,
        target_plan_version=target_plan_version,
        effective_on=effective_on,
        created_by=request.user,
        notes=notes,
    )
    log_audit(
        actor=request.user,
        tenant=tenant,
        action="pricing.transition.scheduled",
        entity_type="PricingTransition",
        entity_id=transition.id,
        metadata={
            "created": created,
            "target_plan_version_id": target_plan_version.id,
            "effective_on": effective_on.isoformat(),
        },
    )
    if created:
        messages.success(request, "Pricing transition scheduled.")
    else:
        messages.success(request, "Matching scheduled transition already exists.")
    return redirect("pricing-list")


@login_required
@require_http_methods(["POST"])
@require_permission("commission.manage")
def pricing_transition_apply(request, transition_id):
    transition = get_object_or_404(PricingTransition, pk=transition_id)
    if not user_can_access_tenant(request.user, transition.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)

    try:
        apply_pricing_transition(transition, actor=request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("pricing-list")

    log_audit(
        actor=request.user,
        tenant=transition.tenant,
        action="pricing.transition.applied",
        entity_type="PricingTransition",
        entity_id=transition.id,
        metadata={
            "target_plan_version_id": transition.target_plan_version_id,
            "effective_on": transition.effective_on.isoformat(),
            "applied_subscription_id": transition.applied_subscription_id,
        },
    )
    messages.success(request, "Pricing transition applied.")
    return redirect("pricing-list")


def _transition_to_dict(row):
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "tenant_code": row.tenant.tenant_code if row.tenant else None,
        "target_plan_version_id": row.target_plan_version_id,
        "target_plan_code": row.target_plan_version.plan.code,
        "target_plan_version": row.target_plan_version.version,
        "effective_on": row.effective_on.isoformat(),
        "status": row.status,
        "source_subscription_id": row.source_subscription_id,
        "applied_subscription_id": row.applied_subscription_id,
        "notes": row.notes,
        "failure_reason": row.failure_reason,
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def pricing_transitions_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)

    if request.method == "GET":
        qs = PricingTransition.objects.select_related("tenant", "target_plan_version__plan")
        tenant_id = request.GET.get("tenant_id")
        status = request.GET.get("status")
        if tenant_id and tenant_id.isdigit():
            qs = qs.filter(tenant_id=int(tenant_id))
        if status in {"scheduled", "applied", "cancelled", "failed"}:
            qs = qs.filter(status=status)
        if not request.user.is_superuser:
            qs = qs.filter(tenant_id__in=get_user_tenant_ids(request.user))
        return JsonResponse({"results": [_transition_to_dict(row) for row in qs[:200]]})

    if not _staff_guard(request.user):
        return JsonResponse({"detail": "Staff access required."}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    tenant_id = payload.get("tenant_id")
    plan_version_id = payload.get("target_plan_version_id")
    if not isinstance(tenant_id, int) or not isinstance(plan_version_id, int):
        return JsonResponse({"detail": "tenant_id and target_plan_version_id are required integers."}, status=400)

    tenant = Tenant.objects.filter(pk=tenant_id).first()
    if tenant is None:
        return JsonResponse({"detail": "tenant_id not found."}, status=404)
    if not user_can_access_tenant(request.user, tenant.id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    target_plan_version = PlanVersion.objects.filter(pk=plan_version_id).first()
    if target_plan_version is None:
        return JsonResponse({"detail": "target_plan_version_id not found."}, status=404)
    try:
        effective_on = _parse_date(payload.get("effective_on"), "effective_on")
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    transition, created = schedule_pricing_transition(
        tenant=tenant,
        target_plan_version=target_plan_version,
        effective_on=effective_on,
        created_by=request.user,
        notes=str(payload.get("notes", "")),
    )
    return JsonResponse(_transition_to_dict(transition), status=201 if created else 200)


@csrf_exempt
@require_http_methods(["POST"])
def pricing_transition_apply_api(request, transition_id):
    if not _staff_guard(request.user):
        return JsonResponse({"detail": "Staff access required."}, status=403)
    transition = PricingTransition.objects.select_related("tenant", "target_plan_version__plan").filter(
        pk=transition_id
    ).first()
    if transition is None:
        return JsonResponse({"detail": "Transition not found."}, status=404)
    if not user_can_access_tenant(request.user, transition.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)

    try:
        apply_pricing_transition(transition, actor=request.user)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    log_audit(
        actor=request.user,
        tenant=transition.tenant,
        action="pricing.transition.applied",
        entity_type="PricingTransition",
        entity_id=transition.id,
        metadata={
            "target_plan_version_id": transition.target_plan_version_id,
            "effective_on": transition.effective_on.isoformat(),
            "applied_subscription_id": transition.applied_subscription_id,
        },
    )
    return JsonResponse(_transition_to_dict(transition))
