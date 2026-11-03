from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.accounts.permissions import require_permission
from apps.accounts.services import get_user_tenant_ids, user_can_access_tenant
from apps.accounts.invitations import invite_business_user_to_tenant
from apps.accounts.models import TenantMembership
from apps.ops.services import log_audit, queue_notification

from .domain_verification import normalize_domain_host, verify_branding_custom_domain
from .forms import BranchForm, TenantBrandingForm, TenantForm, UnitForm
from .forms import DemoTenantRequestForm, DemoTenantRequestReviewForm, TenantUserInvitationForm
from .models import (
    AgreementDocument,
    Branch,
    DemoTenantRequest,
    Module,
    Tenant,
    TenantBranding,
    TenantAgreementAcceptance,
    TenantDatabaseConfiguration,
    TenantModule,
    Unit,
)


def _build_database_configuration(tenant, form, *, demo_mode=False):
    if demo_mode:
        return TenantDatabaseConfiguration(
            tenant=tenant,
            module_code=tenant.module_type,
            mode="managed",
            engine="postgresql",
            activate_tenant_status="trial",
        )

    database_configuration = TenantDatabaseConfiguration(
        tenant=tenant,
        module_code=tenant.module_type,
        mode=form.cleaned_data["database_mode"],
        engine=form.cleaned_data["database_engine"],
        activate_tenant_status=tenant.status,
    )
    if database_configuration.mode == "customer_owned":
        database_configuration.host = form.cleaned_data["database_host"].strip()
        database_configuration.port = form.cleaned_data["database_port"]
        database_configuration.database_name = form.cleaned_data["database_name"].strip()
        database_configuration.username = form.cleaned_data["database_username"].strip()
        database_configuration.ssl_mode = (
            form.cleaned_data.get("database_ssl_mode") or "require"
        ).strip()
        database_configuration.set_password(form.cleaned_data["database_password"])
    return database_configuration


def _create_demo_tenant_from_request(request_row, actor):
    tenant = Tenant.objects.create(
        tenant_code=request_row.requested_tenant_code or f"DEMO-{request_row.id:05d}",
        name=request_row.business_name,
        owner_name=request_row.owner_name,
        owner_email=request_row.owner_email,
        owner_phone=request_row.owner_phone,
        country=request_row.country,
        currency=request_row.currency or "OMR",
        timezone=request_row.timezone or "Asia/Dubai",
        account_type="demo",
        module_type=request_row.module_type,
        pricing_model="subscription",
        commission_enabled=False,
        subscription_status="trial",
        onboarding_date=timezone.localdate(),
        onboarding_fee_paid=False,
        pricing_version="v2",
        status="paused",
        demo_expires_on=timezone.localdate() + timedelta(days=request_row.requested_duration_days),
        demo_notes=request_row.request_notes,
    )
    configuration = TenantDatabaseConfiguration.objects.create(
        tenant=tenant,
        module_code=tenant.module_type,
        mode="managed",
        engine="postgresql",
        activate_tenant_status="trial",
    )
    request_row.status = "approved"
    request_row.approved_tenant = tenant
    request_row.reviewed_by = actor
    request_row.reviewed_at = timezone.now()
    request_row.save(
        update_fields=[
            "status",
            "review_notes",
            "approved_tenant",
            "reviewed_by",
            "reviewed_at",
            "updated_at",
        ]
    )
    return tenant, configuration


def _demo_request_email_recipients(demo_request):
    recipients = [demo_request.owner_email]
    if demo_request.requested_by:
        recipients.append(demo_request.requested_by.email)
    return list(dict.fromkeys(email for email in recipients if email))


def _send_demo_request_decision_email(demo_request, *, approved):
    recipients = _demo_request_email_recipients(demo_request)
    if not recipients:
        return

    if approved:
        tenant = demo_request.approved_tenant
        subject = f"Demo request approved: {demo_request.business_name}"
        message = (
            f"Your demo request for {demo_request.business_name} has been approved.\n\n"
            f"Demo tenant: {tenant.tenant_code}\n"
            f"Expires on: {tenant.demo_expires_on.isoformat()}\n"
        )
    else:
        subject = f"Demo request update: {demo_request.business_name}"
        message = f"Your demo request for {demo_request.business_name} was not approved."

    if demo_request.review_notes:
        message += f"\n\nReview notes:\n{demo_request.review_notes}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=True,
    )


def _marketplace_commission_state(assignment):
    if not assignment or not assignment.enabled:
        return ("Module disabled", "off")
    if not assignment.marketplace_enabled:
        return ("Marketplace off", "off")

    today = timezone.localdate()
    if assignment.commission_grace_until and today <= assignment.commission_grace_until:
        return (f"Grace until {assignment.commission_grace_until.isoformat()}", "pending")
    return ("Commission active", "success")


def _is_valid_branding_domain_host(host):
    if not host:
        return False
    if host in {"localhost", "127.0.0.1"}:
        return False
    if host.replace(".", "").isdigit():
        return False
    return True


@login_required
def tenant_list(request):
    tenants = Tenant.objects.prefetch_related(
        Prefetch("tenant_modules", queryset=TenantModule.objects.select_related("module"))
    )
    if not request.user.is_superuser:
        tenant_ids = get_user_tenant_ids(request.user)
        tenants = tenants.filter(id__in=tenant_ids)

    tenant_rows = []
    for tenant in tenants:
        modules = []
        for tm in tenant.tenant_modules.all():
            if not tm.enabled:
                continue
            state_label, state_class = _marketplace_commission_state(tm)
            modules.append(
                {
                    "name": tm.module.name,
                    "marketplace_enabled": tm.marketplace_enabled,
                    "state_label": state_label,
                    "state_class": state_class,
                }
            )
        tenant_rows.append({"tenant": tenant, "modules": modules})

    return render(
        request,
        "tenants/list.html",
        {"tenants": tenants, "tenant_rows": tenant_rows},
    )


@login_required
@require_permission("tenants.manage")
def tenant_create(request):
    if request.method == "POST":
        form = TenantForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                tenant = form.save(commit=False)
                requested_tenant_status = tenant.status
                tenant.status = "paused"
                tenant.save()
                database_configuration = _build_database_configuration(tenant, form)
                database_configuration.activate_tenant_status = requested_tenant_status
                database_configuration.save()
                if tenant.owner_email:
                    invite_business_user_to_tenant(
                        tenant=tenant,
                        email=tenant.owner_email,
                        full_name=tenant.owner_name,
                        access_level="owner",
                        request=request,
                    )

                from .tasks import provision_tenant_database_task

                transaction.on_commit(
                    lambda configuration_id=database_configuration.id: (
                        provision_tenant_database_task.delay(configuration_id)
                    ),
                    robust=True,
                )
            log_audit(
                actor=request.user,
                tenant=tenant,
                action="tenant.created",
                entity_type="Tenant",
                entity_id=tenant.id,
                metadata={
                    "tenant_code": tenant.tenant_code,
                    "status": tenant.status,
                    "activate_tenant_status": database_configuration.activate_tenant_status,
                    "database_mode": database_configuration.mode,
                    "database_engine": database_configuration.engine,
                },
            )
            queue_notification(
                channel="in_app",
                recipient=tenant.owner_email or "",
                tenant=tenant,
                triggered_by=request.user,
                subject="Tenant onboarding started",
                body=f"Tenant {tenant.name} ({tenant.tenant_code}) was created.",
            )
            return redirect("tenant-list")
    else:
        form = TenantForm()
    return render(
        request,
        "tenants/create.html",
        {
            "form": form,
            "is_demo_flow": False,
            "page_heading": "New Business Registration",
            "submit_label": "Create Tenant",
        },
    )


@login_required
@require_permission("tenants.manage")
def tenant_demo_create(request):
    if request.method == "POST":
        form = TenantForm(request.POST, demo_mode=True)
        if form.is_valid():
            with transaction.atomic():
                tenant = form.save(commit=False)
                tenant.account_type = "demo"
                tenant.pricing_model = "subscription"
                tenant.commission_enabled = False
                tenant.subscription_status = "trial"
                tenant.onboarding_date = timezone.localdate()
                tenant.pricing_version = "v2"
                tenant.status = "paused"
                tenant.demo_expires_on = timezone.localdate() + timedelta(
                    days=form.cleaned_data["demo_duration_days"]
                )
                tenant.save()
                database_configuration = _build_database_configuration(tenant, form, demo_mode=True)
                database_configuration.save()
                if tenant.owner_email:
                    invite_business_user_to_tenant(
                        tenant=tenant,
                        email=tenant.owner_email,
                        full_name=tenant.owner_name,
                        access_level="owner",
                        request=request,
                    )

                from .tasks import provision_tenant_database_task

                transaction.on_commit(
                    lambda configuration_id=database_configuration.id: (
                        provision_tenant_database_task.delay(configuration_id)
                    ),
                    robust=True,
                )
            log_audit(
                actor=request.user,
                tenant=tenant,
                action="tenant.demo.created",
                entity_type="Tenant",
                entity_id=tenant.id,
                metadata={
                    "tenant_code": tenant.tenant_code,
                    "account_type": tenant.account_type,
                    "demo_expires_on": tenant.demo_expires_on.isoformat() if tenant.demo_expires_on else "",
                    "module_type": tenant.module_type,
                },
            )
            queue_notification(
                channel="in_app",
                recipient=tenant.owner_email or "",
                tenant=tenant,
                triggered_by=request.user,
                subject="Demo tenant onboarding started",
                body=(
                    f"Demo tenant {tenant.name} ({tenant.tenant_code}) was created and will expire on "
                    f"{tenant.demo_expires_on.isoformat()}."
                ),
            )
            messages.success(
                request,
                f"Demo tenant {tenant.tenant_code} created with expiry {tenant.demo_expires_on.isoformat()}.",
            )
            return redirect("tenant-list")
    else:
        form = TenantForm(
            initial={"account_type": "demo"},
            demo_mode=True,
        )
    return render(
        request,
        "tenants/create.html",
        {
            "form": form,
            "is_demo_flow": True,
            "page_heading": "New Demo Tenant",
            "submit_label": "Create Demo Tenant",
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def demo_request_create(request):
    if request.method == "POST":
        form = DemoTenantRequestForm(request.POST)
        if form.is_valid():
            demo_request = form.save(commit=False)
            demo_request.requested_by = request.user
            demo_request.status = "requested"
            demo_request.source = "central"
            demo_request.product_interest = demo_request.module_type
            demo_request.save()
            log_audit(
                actor=request.user,
                action="tenant.demo.requested",
                entity_type="DemoTenantRequest",
                entity_id=demo_request.id,
                metadata={
                    "business_name": demo_request.business_name,
                    "module_type": demo_request.module_type,
                    "requested_duration_days": demo_request.requested_duration_days,
                },
            )
            queue_notification(
                channel="in_app",
                recipient="ops",
                triggered_by=request.user,
                subject="Demo tenant request submitted",
                body=f"Demo request #{demo_request.id} submitted for {demo_request.business_name}.",
            )
            messages.success(request, "Demo request submitted. Central approval is required before activation.")
            return redirect("my-demo-requests")
    else:
        form = DemoTenantRequestForm()
    return render(request, "tenants/demo_request_create.html", {"form": form})


@login_required
def my_demo_requests(request):
    requests_qs = DemoTenantRequest.objects.filter(
        requested_by=request.user,
    ).select_related("reviewed_by", "approved_tenant").order_by("-created_at")
    return render(
        request,
        "tenants/my_demo_requests.html",
        {"demo_requests": requests_qs[:200]},
    )


@login_required
@require_permission("tenants.manage")
def demo_request_list(request):
    requests_qs = DemoTenantRequest.objects.select_related(
        "requested_by",
        "reviewed_by",
        "approved_tenant",
    ).order_by("status", "-created_at")
    review_form = DemoTenantRequestReviewForm()
    return render(
        request,
        "tenants/demo_request_list.html",
        {
            "demo_requests": requests_qs[:200],
            "review_form": review_form,
        },
    )


@login_required
@require_permission("tenants.manage")
@require_http_methods(["POST"])
def demo_request_review(request, request_id):
    demo_request = DemoTenantRequest.objects.filter(pk=request_id).first()
    if demo_request is None:
        raise Http404("Demo request not found")
    if demo_request.status != "requested":
        messages.error(request, "Only requested demo records can be reviewed.")
        return redirect("demo-request-list")

    form = DemoTenantRequestReviewForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Review form is invalid.")
        return redirect("demo-request-list")

    action = form.cleaned_data["action"]
    review_notes = (form.cleaned_data.get("review_notes") or "").strip()
    selected_module_type = (form.cleaned_data.get("module_type") or "").strip()
    if action == "approve":
        target_module_type = selected_module_type or demo_request.module_type
        valid_module_types = dict(Tenant.MODULE_TYPE_CHOICES)
        if target_module_type not in valid_module_types:
            messages.error(
                request,
                "Select a target business module before approving this request.",
            )
            return redirect("demo-request-list")
        if not demo_request.owner_email:
            messages.error(request, "A business owner email is required before approval.")
            return redirect("demo-request-list")

    with transaction.atomic():
        demo_request.review_notes = review_notes
        if action == "approve":
            demo_request.module_type = target_module_type
            if not demo_request.product_interest:
                demo_request.product_interest = target_module_type
            demo_request.save(update_fields=["module_type", "product_interest", "updated_at"])
            tenant, configuration = _create_demo_tenant_from_request(demo_request, request.user)
            invitation = invite_business_user_to_tenant(
                tenant=tenant,
                email=demo_request.owner_email,
                full_name=demo_request.owner_name,
                access_level="owner",
                request=request,
            )

            from .tasks import provision_tenant_database_task

            transaction.on_commit(
                lambda configuration_id=configuration.id: (
                    provision_tenant_database_task.delay(configuration_id)
                ),
                robust=True,
            )
            log_audit(
                actor=request.user,
                tenant=tenant,
                action="tenant.demo.request.approved",
                entity_type="DemoTenantRequest",
                entity_id=demo_request.id,
                metadata={
                    "approved_tenant_id": tenant.id,
                    "approved_tenant_code": tenant.tenant_code,
                    "invited_user_id": invitation.user.id,
                },
            )
            queue_notification(
                channel="in_app",
                recipient=demo_request.owner_email or "",
                tenant=tenant,
                triggered_by=request.user,
                subject="Demo request approved",
                body=(
                    f"Your demo request for {demo_request.business_name} was approved. "
                    f"Demo tenant {tenant.tenant_code} expires on {tenant.demo_expires_on.isoformat()}."
                ),
            )
            transaction.on_commit(
                lambda request_id=demo_request.id: _send_demo_request_decision_email(
                    DemoTenantRequest.objects.select_related(
                        "requested_by", "approved_tenant"
                    ).get(pk=request_id),
                    approved=True,
                ),
                robust=True,
            )
            messages.success(request, f"Demo request #{demo_request.id} approved.")
        else:
            demo_request.status = "rejected"
            demo_request.reviewed_by = request.user
            demo_request.reviewed_at = timezone.now()
            demo_request.save(
                update_fields=[
                    "status",
                    "review_notes",
                    "reviewed_by",
                    "reviewed_at",
                    "updated_at",
                ]
            )
            log_audit(
                actor=request.user,
                action="tenant.demo.request.rejected",
                entity_type="DemoTenantRequest",
                entity_id=demo_request.id,
                metadata={"business_name": demo_request.business_name},
            )
            queue_notification(
                channel="in_app",
                recipient=demo_request.owner_email or "",
                triggered_by=request.user,
                subject="Demo request reviewed",
                body=f"Your demo request for {demo_request.business_name} was not approved.",
            )
            transaction.on_commit(
                lambda request_id=demo_request.id: _send_demo_request_decision_email(
                    DemoTenantRequest.objects.select_related("requested_by").get(pk=request_id),
                    approved=False,
                ),
                robust=True,
            )
            messages.success(request, f"Demo request #{demo_request.id} rejected.")

    return redirect("demo-request-list")


@login_required
@require_permission("tenants.manage")
@require_http_methods(["GET", "POST"])
def tenant_users_manage(request, tenant_id):
    if not user_can_access_tenant(request.user, tenant_id):
        raise Http404("Tenant not found")
    tenant = Tenant.objects.filter(pk=tenant_id).first()
    if tenant is None:
        raise Http404("Tenant not found")

    if request.method == "POST":
        form = TenantUserInvitationForm(request.POST)
        if form.is_valid():
            try:
                result = invite_business_user_to_tenant(
                    tenant=tenant,
                    email=form.cleaned_data["email"],
                    full_name=form.cleaned_data["full_name"],
                    access_level=form.cleaned_data["access_level"],
                    request=request,
                )
            except ValueError as exc:
                form.add_error("email", str(exc))
            else:
                log_audit(
                    actor=request.user,
                    tenant=tenant,
                    action="tenant.user.invited",
                    entity_type="TenantMembership",
                    entity_id=result.membership.id,
                    metadata={
                        "user_id": result.user.id,
                        "email": result.user.email,
                        "access_level": form.cleaned_data["access_level"],
                        "invitation_required": result.invitation_required,
                    },
                )
                messages.success(
                    request,
                    "Invitation sent." if result.invitation_required else "Existing account access activated.",
                )
                return redirect("tenant-users-manage", tenant_id=tenant.id)
    else:
        form = TenantUserInvitationForm(
            initial={"access_level": "member"},
        )

    memberships = TenantMembership.objects.filter(tenant=tenant).select_related("user").prefetch_related(
        "membership_roles__role"
    )
    return render(
        request,
        "tenants/users_manage.html",
        {"tenant": tenant, "memberships": memberships, "form": form},
    )


@login_required
@require_permission("tenants.manage")
@require_http_methods(["POST"])
def demo_request_convert_to_paid(request, request_id):
    with transaction.atomic():
        demo_request = DemoTenantRequest.objects.select_for_update().select_related(
            "approved_tenant"
        ).filter(pk=request_id).first()
        if demo_request is None:
            raise Http404("Demo request not found")
        if demo_request.status != "approved" or not demo_request.approved_tenant:
            messages.error(request, "Only approved demo requests can be converted.")
            return redirect("demo-request-list")

        tenant = Tenant.objects.select_for_update().get(pk=demo_request.approved_tenant_id)
        if not tenant.is_demo:
            messages.info(request, f"Tenant {tenant.tenant_code} is already a production tenant.")
            return redirect("demo-request-list")

        tenant.account_type = "production"
        tenant.status = "active"
        tenant.subscription_status = "active"
        tenant.commission_enabled = True
        tenant.demo_expires_on = None
        tenant.demo_converted_to_paid_at = timezone.now()
        tenant.save(
            update_fields=[
                "account_type",
                "status",
                "subscription_status",
                "commission_enabled",
                "demo_expires_on",
                "demo_converted_to_paid_at",
                "updated_at",
            ]
        )
        log_audit(
            actor=request.user,
            tenant=tenant,
            action="tenant.demo.converted_to_paid",
            entity_type="Tenant",
            entity_id=tenant.id,
            metadata={"demo_request_id": demo_request.id, "tenant_code": tenant.tenant_code},
        )

    messages.success(request, f"Tenant {tenant.tenant_code} converted to paid production.")
    return redirect("demo-request-list")


@login_required
@require_permission("modules.assign")
def tenant_modules_manage(request, tenant_id):
    if not user_can_access_tenant(request.user, tenant_id):
        raise Http404("Tenant not found")
    try:
        tenant = Tenant.objects.get(pk=tenant_id)
    except Tenant.DoesNotExist as exc:
        raise Http404("Tenant not found") from exc

    modules = list(Module.objects.filter(is_active=True).order_by("name"))
    current = {
        item.module_id: item
        for item in TenantModule.objects.filter(tenant=tenant).select_related("module")
    }

    if request.method == "POST":
        enabled_ids = {int(v) for v in request.POST.getlist("modules") if v.isdigit()}
        marketplace_ids = {
            int(v) for v in request.POST.getlist("marketplace_modules") if v.isdigit()
        }
        free_days = int(getattr(settings, "MARKETPLACE_FREE_DAYS", 60))

        with transaction.atomic():
            for module in modules:
                tenant_module = current.get(module.id)
                enabled = module.id in enabled_ids
                marketplace_enabled = enabled and (module.id in marketplace_ids)
                now = timezone.now()
                grace_until = (now + timedelta(days=free_days)).date()

                if tenant_module is None:
                    TenantModule.objects.create(
                        tenant=tenant,
                        module=module,
                        enabled=enabled,
                        marketplace_enabled=marketplace_enabled,
                        marketplace_activated_at=now if marketplace_enabled else None,
                        commission_grace_until=grace_until if marketplace_enabled else None,
                    )
                else:
                    if (
                        marketplace_enabled
                        and not tenant_module.marketplace_enabled
                        and tenant_module.marketplace_activated_at is None
                    ):
                        tenant_module.marketplace_activated_at = now
                        tenant_module.commission_grace_until = grace_until
                    tenant_module.enabled = enabled
                    tenant_module.marketplace_enabled = marketplace_enabled
                    tenant_module.save(
                        update_fields=[
                            "enabled",
                            "marketplace_enabled",
                            "marketplace_activated_at",
                            "commission_grace_until",
                        ]
                    )
        enabled_codes = [
            module.code for module in modules if module.id in enabled_ids
        ]
        marketplace_codes = [
            module.code for module in modules if module.id in marketplace_ids and module.id in enabled_ids
        ]
        log_audit(
            actor=request.user,
            tenant=tenant,
            action="tenant.modules.updated",
            entity_type="Tenant",
            entity_id=tenant.id,
            metadata={
                "enabled_modules": enabled_codes,
                "marketplace_modules": marketplace_codes,
            },
        )
        queue_notification(
            channel="in_app",
            recipient=tenant.owner_email or "",
            tenant=tenant,
            triggered_by=request.user,
            subject="Module access updated",
            body=f"Enabled modules: {', '.join(enabled_codes) if enabled_codes else 'none'}.",
        )

        messages.success(request, "Tenant modules updated successfully.")
        return redirect("tenant-modules-manage", tenant_id=tenant.id)

    rows = []
    for module in modules:
        assignment = current.get(module.id)
        state_label, state_class = _marketplace_commission_state(assignment)
        rows.append(
            {
                "module": module,
                "enabled": bool(assignment.enabled) if assignment else False,
                "marketplace_enabled": bool(assignment.marketplace_enabled)
                if assignment
                else False,
                "marketplace_activated_at": assignment.marketplace_activated_at if assignment else None,
                "commission_grace_until": assignment.commission_grace_until if assignment else None,
                "commission_state_label": state_label,
                "commission_state_class": state_class,
            }
        )

    return render(
        request,
        "tenants/modules_manage.html",
        {
            "tenant": tenant,
            "rows": rows,
        },
    )


@login_required
def agreement_list(request):
    tenant = getattr(request, "active_tenant", None)
    if tenant is None:
        if request.user.is_superuser:
            tenant = Tenant.objects.first()
        else:
            tenant_ids = get_user_tenant_ids(request.user)
            tenant = Tenant.objects.filter(id__in=tenant_ids).first()

    if tenant is None:
        return render(
            request,
            "tenants/agreements.html",
            {"tenant": None, "rows": []},
        )

    docs = AgreementDocument.objects.filter(is_active=True)
    accepted_ids = set(
        TenantAgreementAcceptance.objects.filter(tenant=tenant).values_list(
            "document_id", flat=True
        )
    )
    rows = [{"document": d, "accepted": d.id in accepted_ids} for d in docs]
    return render(
        request,
        "tenants/agreements.html",
        {
            "tenant": tenant,
            "rows": rows,
        },
    )


@login_required
@require_permission("tenants.manage")
@require_http_methods(["POST"])
def agreement_accept(request, doc_id):
    tenant = getattr(request, "active_tenant", None)
    if tenant is None:
        messages.error(request, "Select an active tenant first.")
        return redirect("tenant-agreements")

    if not user_can_access_tenant(request.user, tenant.id):
        raise Http404("Tenant not found")

    document = AgreementDocument.objects.filter(pk=doc_id, is_active=True).first()
    if document is None:
        messages.error(request, "Agreement document not found.")
        return redirect("tenant-agreements")

    TenantAgreementAcceptance.objects.get_or_create(
        tenant=tenant,
        document=document,
        defaults={
            "accepted_by": request.user,
            "ip_address": request.META.get("REMOTE_ADDR", "")[:64],
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
        },
    )
    log_audit(
        actor=request.user,
        tenant=tenant,
        action="legal.agreement.accepted",
        entity_type="AgreementDocument",
        entity_id=document.id,
        metadata={"code": document.code, "version": document.version},
    )
    queue_notification(
        channel="in_app",
        recipient=tenant.owner_email or "",
        tenant=tenant,
        triggered_by=request.user,
        subject="Agreement accepted",
        body=f"{document.title} ({document.version}) accepted for {tenant.name}.",
    )
    messages.success(request, "Agreement accepted and recorded.")
    return redirect("tenant-agreements")


@login_required
@require_permission("tenants.manage")
def tenant_structure_manage(request, tenant_id):
    if not user_can_access_tenant(request.user, tenant_id):
        raise Http404("Tenant not found")

    tenant = Tenant.objects.filter(pk=tenant_id).first()
    if tenant is None:
        raise Http404("Tenant not found")

    branch_qs = Branch.objects.filter(tenant=tenant).order_by("name")
    unit_qs = Unit.objects.filter(tenant=tenant).select_related("branch").order_by("branch__name", "name")

    if request.method == "POST":
        form_type = request.POST.get("form_type", "").strip()
        if form_type == "branch":
            branch_form = BranchForm(request.POST)
            unit_form = UnitForm(branch_queryset=branch_qs)
            if branch_form.is_valid():
                branch = branch_form.save(commit=False)
                branch.tenant = tenant
                branch.save()
                log_audit(
                    actor=request.user,
                    tenant=tenant,
                    action="tenant.branch.created",
                    entity_type="Branch",
                    entity_id=branch.id,
                    metadata={"code": branch.code, "name": branch.name},
                )
                messages.success(request, "Branch created.")
                return redirect("tenant-structure-manage", tenant_id=tenant.id)
        elif form_type == "unit":
            branch_form = BranchForm()
            unit_form = UnitForm(request.POST, branch_queryset=branch_qs)
            if unit_form.is_valid():
                unit = unit_form.save(commit=False)
                unit.tenant = tenant
                if unit.branch.tenant_id != tenant.id:
                    messages.error(request, "Selected branch does not belong to this tenant.")
                    return redirect("tenant-structure-manage", tenant_id=tenant.id)
                unit.save()
                log_audit(
                    actor=request.user,
                    tenant=tenant,
                    action="tenant.unit.created",
                    entity_type="Unit",
                    entity_id=unit.id,
                    metadata={"code": unit.code, "name": unit.name, "branch_id": unit.branch_id},
                )
                messages.success(request, "Unit created.")
                return redirect("tenant-structure-manage", tenant_id=tenant.id)
        else:
            branch_form = BranchForm()
            unit_form = UnitForm(branch_queryset=branch_qs)
            messages.error(request, "Unsupported structure form action.")
    else:
        branch_form = BranchForm()
        unit_form = UnitForm(branch_queryset=branch_qs)

    return render(
        request,
        "tenants/structure_manage.html",
        {
            "tenant": tenant,
            "branches": branch_qs[:200],
            "units": unit_qs[:400],
            "branch_form": branch_form,
            "unit_form": unit_form,
        },
    )


@login_required
@require_permission("tenants.manage")
def tenant_branding_manage(request, tenant_id):
    if not user_can_access_tenant(request.user, tenant_id):
        raise Http404("Tenant not found")

    tenant = Tenant.objects.filter(pk=tenant_id).first()
    if tenant is None:
        raise Http404("Tenant not found")

    branding, _ = TenantBranding.objects.get_or_create(
        tenant=tenant,
        defaults={
            "brand_name": tenant.name,
            "primary_color": "#0f766e",
            "accent_color": "#0369a1",
        },
    )

    if request.method == "POST":
        form = TenantBrandingForm(request.POST, instance=branding)
        if form.is_valid():
            previous_domain = normalize_domain_host(branding.custom_domain)
            branding = form.save()
            new_domain = normalize_domain_host(branding.custom_domain)
            if not new_domain:
                branding.domain_verification_status = "not_configured"
                branding.domain_verification_token = ""
                branding.domain_verified_at = None
                branding.domain_last_checked_at = timezone.now()
                branding.domain_failure_reason = ""
                branding.save(
                    update_fields=[
                        "domain_verification_status",
                        "domain_verification_token",
                        "domain_verified_at",
                        "domain_last_checked_at",
                        "domain_failure_reason",
                        "updated_at",
                    ]
                )
            elif new_domain != previous_domain:
                branding.domain_verification_status = "pending"
                branding.domain_verification_token = TenantBranding.generate_domain_verification_token()
                branding.domain_verified_at = None
                branding.domain_last_checked_at = timezone.now()
                branding.domain_failure_reason = ""
                branding.save(
                    update_fields=[
                        "custom_domain",
                        "domain_verification_status",
                        "domain_verification_token",
                        "domain_verified_at",
                        "domain_last_checked_at",
                        "domain_failure_reason",
                        "updated_at",
                    ]
                )
            log_audit(
                actor=request.user,
                tenant=tenant,
                action="tenant.branding.updated",
                entity_type="TenantBranding",
                entity_id=branding.id,
                metadata={
                    "brand_name": branding.brand_name,
                    "custom_domain": branding.custom_domain,
                    "domain_verification_status": branding.domain_verification_status,
                    "is_active": branding.is_active,
                },
            )
            messages.success(request, "Tenant branding updated.")
            return redirect("tenant-branding-manage", tenant_id=tenant.id)
    else:
        form = TenantBrandingForm(instance=branding)

    return render(
        request,
        "tenants/branding_manage.html",
        {
            "tenant": tenant,
            "form": form,
            "branding": branding,
        },
    )


@login_required
@require_permission("tenants.manage")
@require_http_methods(["POST"])
def tenant_branding_domain_refresh_token(request, tenant_id):
    if not user_can_access_tenant(request.user, tenant_id):
        raise Http404("Tenant not found")
    branding = TenantBranding.objects.select_related("tenant").filter(tenant_id=tenant_id).first()
    if branding is None:
        raise Http404("Tenant branding not found")

    host = normalize_domain_host(branding.custom_domain)
    if not _is_valid_branding_domain_host(host):
        messages.error(request, "Set a valid custom domain first.")
        return redirect("tenant-branding-manage", tenant_id=tenant_id)

    branding.domain_verification_status = "pending"
    branding.domain_verification_token = TenantBranding.generate_domain_verification_token()
    branding.domain_verified_at = None
    branding.domain_last_checked_at = timezone.now()
    branding.domain_failure_reason = ""
    branding.save(
        update_fields=[
            "domain_verification_status",
            "domain_verification_token",
            "domain_verified_at",
            "domain_last_checked_at",
            "domain_failure_reason",
            "updated_at",
        ]
    )
    log_audit(
        actor=request.user,
        tenant=branding.tenant,
        action="tenant.branding.domain.token_refreshed",
        entity_type="TenantBranding",
        entity_id=branding.id,
        metadata={"custom_domain": host},
    )
    messages.success(request, "Domain verification token refreshed.")
    return redirect("tenant-branding-manage", tenant_id=tenant_id)


@login_required
@require_permission("tenants.manage")
@require_http_methods(["POST"])
def tenant_branding_domain_verify(request, tenant_id):
    if not user_can_access_tenant(request.user, tenant_id):
        raise Http404("Tenant not found")
    branding = TenantBranding.objects.select_related("tenant").filter(tenant_id=tenant_id).first()
    if branding is None:
        raise Http404("Tenant branding not found")

    host = normalize_domain_host(branding.custom_domain)
    if not _is_valid_branding_domain_host(host):
        messages.error(request, "Set a valid custom domain first.")
        return redirect("tenant-branding-manage", tenant_id=tenant_id)
    result = verify_branding_custom_domain(branding)
    log_audit(
        actor=request.user,
        tenant=branding.tenant,
        action="tenant.branding.domain.verified" if result["verified"] else "tenant.branding.domain.verify_failed",
        entity_type="TenantBranding",
        entity_id=branding.id,
        metadata={"custom_domain": host, "verified": result["verified"], "reason": result["reason"]},
    )
    if result["verified"]:
        messages.success(request, "Custom domain verified.")
    else:
        messages.error(request, f"Custom domain verification failed: {result['reason']}")
    return redirect("tenant-branding-manage", tenant_id=tenant_id)


@require_http_methods(["GET"])
def tenant_branding_domain_status_api(request, tenant_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)
    if not user_can_access_tenant(request.user, tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)

    branding = TenantBranding.objects.filter(tenant_id=tenant_id).first()
    if branding is None:
        return JsonResponse({"detail": "Branding not found."}, status=404)

    return JsonResponse(
        {
            "tenant_id": tenant_id,
            "custom_domain": branding.custom_domain,
            "domain_verification_status": branding.domain_verification_status,
            "domain_verification_token": branding.domain_verification_token,
            "domain_txt_record_value": branding.domain_txt_record_value,
            "domain_verified_at": branding.domain_verified_at.isoformat() if branding.domain_verified_at else None,
            "domain_last_checked_at": (
                branding.domain_last_checked_at.isoformat() if branding.domain_last_checked_at else None
            ),
            "domain_failure_reason": branding.domain_failure_reason,
        }
    )
