import json
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.accounts.permissions import require_permission
from apps.accounts.services import get_user_tenant_ids, user_can_access_tenant
from apps.ops.services import log_audit, queue_notification
from apps.tenants.models import Tenant, Unit

from .forms import StayBookingCreateForm, StayExtensionRequestForm, StayUnitRateForm
from .models import StayBooking, StayUnitAvailability, StayUnitRate
from .services import create_stay_booking, extension_preview, extend_stay_booking


def _parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}, expected YYYY-MM-DD")


def _booking_to_dict(booking):
    commission = getattr(booking, "commission_record", None)
    return {
        "id": booking.id,
        "booking_id": booking.booking_id,
        "tenant_id": booking.tenant_id,
        "tenant_code": booking.tenant.tenant_code,
        "unit_id": booking.unit_id,
        "unit_code": booking.unit.code,
        "unit_name": booking.unit.name,
        "booking_type": booking.booking_type,
        "parent_booking_id": booking.parent_booking_id,
        "check_in": booking.check_in.isoformat(),
        "check_out": booking.check_out.isoformat(),
        "nights": booking.nights,
        "customer_name": booking.customer_name,
        "customer_email": booking.customer_email,
        "status": booking.status,
        "payment_rule": booking.payment_rule,
        "payment_status": booking.payment_status,
        "subtotal_amount": str(booking.subtotal_amount),
        "tax_amount": str(booking.tax_amount),
        "total_amount": str(booking.total_amount),
        "currency": booking.currency,
        "commission_rate": str(commission.commission_rate) if commission else "0.00",
        "commission_amount": str(commission.commission_amount) if commission else "0.00",
        "created_at": booking.created_at.isoformat(),
    }


@login_required
def customer_dashboard(request):
    account_email = (request.user.email or "").strip().lower()
    requested_email = (request.GET.get("customer_email") or "").strip().lower()
    customer_email = requested_email if request.user.is_staff else account_email
    bookings = StayBooking.objects.select_related("tenant", "unit", "commission_record")
    if customer_email:
        bookings = bookings.filter(customer_email__iexact=customer_email)
    else:
        bookings = bookings.none()
    bookings = bookings.order_by("-created_at")[:100]
    return render(
        request,
        "stay/customer_dashboard.html",
        {"bookings": bookings, "customer_email": customer_email},
    )


@login_required
@require_permission("billing.settle")
def business_dashboard(request):
    tenant_ids = get_user_tenant_ids(request.user) if not request.user.is_superuser else None
    active_tenant = getattr(request, "active_tenant", None)
    bookings = StayBooking.objects.select_related("tenant", "unit", "parent_booking", "commission_record")
    if tenant_ids is not None:
        bookings = bookings.filter(tenant_id__in=tenant_ids)
    if active_tenant:
        bookings = bookings.filter(tenant=active_tenant)

    if request.method == "POST":
        if request.POST.get("form_type") == "create_booking":
            form = StayBookingCreateForm(request.POST)
            if form.is_valid():
                tenant = form.cleaned_data["tenant"]
                unit = form.cleaned_data["unit"]
                if not user_can_access_tenant(request.user, tenant.id):
                    return JsonResponse({"detail": "Tenant access denied."}, status=403)
                if unit.tenant_id != tenant.id:
                    messages.error(request, "Selected unit does not belong to selected tenant.")
                    return redirect("stay-business-dashboard")
                booking = create_stay_booking(
                    tenant=tenant,
                    unit=unit,
                    check_in=form.cleaned_data["check_in"],
                    check_out=form.cleaned_data["check_out"],
                    payment_rule=form.cleaned_data["payment_rule"],
                    customer_name=form.cleaned_data.get("customer_name", ""),
                    customer_email=form.cleaned_data.get("customer_email", ""),
                    customer_phone=form.cleaned_data.get("customer_phone", ""),
                    guests=form.cleaned_data.get("guests", 1),
                    notes=form.cleaned_data.get("notes", ""),
                    created_by=request.user,
                )
                log_audit(
                    actor=request.user,
                    tenant=booking.tenant,
                    module=booking.module,
                    action="stay.booking.created",
                    entity_type="StayBooking",
                    entity_id=booking.id,
                    metadata={"booking_id": booking.booking_id, "total_amount": str(booking.total_amount)},
                )
                queue_notification(
                    channel="in_app",
                    recipient=booking.customer_email or "",
                    tenant=booking.tenant,
                    module=booking.module,
                    triggered_by=request.user,
                    subject="Stay booking confirmed",
                    body=f"Booking {booking.booking_id} confirmed from {booking.check_in} to {booking.check_out}.",
                )
                queue_notification(
                    channel="in_app",
                    recipient=booking.tenant.owner_email or "",
                    tenant=booking.tenant,
                    module=booking.module,
                    triggered_by=request.user,
                    subject="New stay booking",
                    body=f"Booking {booking.booking_id} created for {booking.total_amount} {booking.currency}.",
                )
                messages.success(request, f"Booking {booking.booking_id} created.")
                return redirect("stay-business-dashboard")
        elif request.POST.get("form_type") == "extend_booking":
            ext_form = StayExtensionRequestForm(request.POST)
            if ext_form.is_valid():
                parent = StayBooking.objects.select_related("tenant", "module", "unit").filter(
                    pk=ext_form.cleaned_data["parent_booking_id"]
                ).first()
                if parent is None:
                    messages.error(request, "Parent booking not found.")
                    return redirect("stay-business-dashboard")
                if not user_can_access_tenant(request.user, parent.tenant_id):
                    return JsonResponse({"detail": "Tenant access denied."}, status=403)
                try:
                    extension, _preview = extend_stay_booking(
                        parent_booking=parent,
                        new_check_out=ext_form.cleaned_data["new_check_out"],
                        payment_rule=ext_form.cleaned_data["payment_rule"],
                        selected_unit_id=ext_form.cleaned_data.get("selected_unit_id"),
                        notes=ext_form.cleaned_data.get("notes", ""),
                        created_by=request.user,
                    )
                except ValueError as exc:
                    messages.error(request, str(exc))
                    return redirect("stay-business-dashboard")
                log_audit(
                    actor=request.user,
                    tenant=extension.tenant,
                    module=extension.module,
                    action="stay.booking.extended",
                    entity_type="StayBooking",
                    entity_id=extension.id,
                    metadata={
                        "booking_id": extension.booking_id,
                        "parent_booking_id": extension.parent_booking_id,
                        "payment_rule": extension.payment_rule,
                    },
                )
                queue_notification(
                    channel="in_app",
                    recipient=extension.customer_email or "",
                    tenant=extension.tenant,
                    module=extension.module,
                    triggered_by=request.user,
                    subject="Stay extension confirmed",
                    body=(
                        f"Extension booking {extension.booking_id} confirmed from "
                        f"{extension.check_in} to {extension.check_out}."
                    ),
                )
                queue_notification(
                    channel="in_app",
                    recipient=extension.tenant.owner_email or "",
                    tenant=extension.tenant,
                    module=extension.module,
                    triggered_by=request.user,
                    subject="Stay extension created",
                    body=(
                        f"Extension booking {extension.booking_id} linked to "
                        f"{parent.booking_id} for {extension.total_amount} {extension.currency}."
                    ),
                )
                messages.success(
                    request,
                    f"Extension booking {extension.booking_id} created and linked to {parent.booking_id}.",
                )
                return redirect("stay-business-dashboard")
    create_form = StayBookingCreateForm()
    ext_form = StayExtensionRequestForm()
    rate_form = StayUnitRateForm()
    if tenant_ids is not None:
        create_form.fields["tenant"].queryset = create_form.fields["tenant"].queryset.filter(id__in=tenant_ids)
        rate_form.fields["tenant"].queryset = rate_form.fields["tenant"].queryset.filter(id__in=tenant_ids)
    if active_tenant:
        create_form.fields["tenant"].initial = active_tenant.id
        create_form.fields["tenant"].queryset = create_form.fields["tenant"].queryset.filter(id=active_tenant.id)
        rate_form.fields["tenant"].initial = active_tenant.id
        rate_form.fields["tenant"].queryset = rate_form.fields["tenant"].queryset.filter(id=active_tenant.id)

    return render(
        request,
        "stay/business_dashboard.html",
        {
            "bookings": bookings.order_by("-created_at")[:200],
            "create_form": create_form,
            "extension_form": ext_form,
            "rate_form": rate_form,
        },
    )


@login_required
@require_permission("reports.view")
def admin_panel(request):
    bookings = StayBooking.objects.select_related("tenant", "unit", "parent_booking", "commission_record")
    totals = bookings.aggregate(
        gross=Sum("total_amount"),
        extension_revenue=Sum("total_amount", filter=Q(booking_type="extension")),
        original_revenue=Sum("total_amount", filter=Q(booking_type="original")),
    )
    return render(
        request,
        "stay/admin_panel.html",
        {"bookings": bookings.order_by("-created_at")[:300], "totals": totals},
    )


@login_required
@require_permission("reports.view")
def report_view(request):
    tenant_id = request.GET.get("tenant_id")
    qs = StayBooking.objects.all()
    if tenant_id and tenant_id.isdigit():
        qs = qs.filter(tenant_id=int(tenant_id))
    if not request.user.is_superuser:
        qs = qs.filter(tenant_id__in=get_user_tenant_ids(request.user))
    totals = qs.aggregate(
        original_revenue=Sum("total_amount", filter=Q(booking_type="original")),
        extension_revenue=Sum("total_amount", filter=Q(booking_type="extension")),
        extension_count=Count("id", filter=Q(booking_type="extension")),
    )
    return render(request, "stay/report.html", {"totals": totals, "rows": qs.order_by("-created_at")[:500]})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def bookings_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)

    if request.method == "GET":
        qs = StayBooking.objects.select_related("tenant", "unit", "commission_record")
        tenant_id = request.GET.get("tenant_id")
        customer_email = (request.GET.get("customer_email") or "").strip()
        if tenant_id and tenant_id.isdigit():
            if not user_can_access_tenant(request.user, int(tenant_id)):
                return JsonResponse({"detail": "Tenant access denied."}, status=403)
            qs = qs.filter(tenant_id=int(tenant_id))
        elif not request.user.is_superuser:
            qs = qs.filter(tenant_id__in=get_user_tenant_ids(request.user))
        if customer_email:
            qs = qs.filter(customer_email__iexact=customer_email)
        return JsonResponse({"results": [_booking_to_dict(row) for row in qs[:300]]})

    if not request.user.is_superuser and not request.user.is_staff:
        return JsonResponse({"detail": "Staff access required."}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    tenant_id = payload.get("tenant_id")
    unit_id = payload.get("unit_id")
    if not isinstance(tenant_id, int) or not isinstance(unit_id, int):
        return JsonResponse({"detail": "tenant_id and unit_id are required integers."}, status=400)
    if not user_can_access_tenant(request.user, tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    try:
        tenant = Tenant.objects.get(pk=tenant_id)
        unit = Unit.objects.get(pk=unit_id, tenant_id=tenant_id)
        booking = create_stay_booking(
            tenant=tenant,
            unit=unit,
            check_in=_parse_date(payload.get("check_in"), "check_in"),
            check_out=_parse_date(payload.get("check_out"), "check_out"),
            payment_rule=str(payload.get("payment_rule") or "pay_now"),
            customer_name=str(payload.get("customer_name", "")),
            customer_email=str(payload.get("customer_email", "")),
            customer_phone=str(payload.get("customer_phone", "")),
            guests=int(payload.get("guests", 1)),
            notes=str(payload.get("notes", "")),
            created_by=request.user,
        )
    except Exception as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse(_booking_to_dict(booking), status=201)


@csrf_exempt
@require_http_methods(["POST"])
def extension_preview_api(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)
    booking = get_object_or_404(StayBooking.objects.select_related("tenant", "unit"), pk=booking_id)
    if not user_can_access_tenant(request.user, booking.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")
    try:
        preview = extension_preview(
            parent_booking=booking,
            new_check_out=_parse_date(payload.get("new_check_out"), "new_check_out"),
        )
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    return JsonResponse(preview)


@csrf_exempt
@require_http_methods(["POST"])
def extension_create_api(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)
    booking = get_object_or_404(StayBooking.objects.select_related("tenant", "module", "unit"), pk=booking_id)
    if not user_can_access_tenant(request.user, booking.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    try:
        extension, preview = extend_stay_booking(
            parent_booking=booking,
            new_check_out=_parse_date(payload.get("new_check_out"), "new_check_out"),
            payment_rule=str(payload.get("payment_rule") or "pay_now"),
            selected_unit_id=payload.get("selected_unit_id"),
            notes=str(payload.get("notes", "")),
            created_by=request.user,
        )
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    log_audit(
        actor=request.user,
        tenant=extension.tenant,
        module=extension.module,
        action="stay.booking.extended",
        entity_type="StayBooking",
        entity_id=extension.id,
        metadata={
            "booking_id": extension.booking_id,
            "parent_booking_id": extension.parent_booking_id,
            "payment_rule": extension.payment_rule,
        },
    )
    queue_notification(
        channel="in_app",
        recipient=extension.customer_email or "",
        tenant=extension.tenant,
        module=extension.module,
        triggered_by=request.user,
        subject="Stay extension confirmed",
        body=f"Extension booking {extension.booking_id} confirmed.",
    )
    queue_notification(
        channel="in_app",
        recipient=extension.tenant.owner_email or "",
        tenant=extension.tenant,
        module=extension.module,
        triggered_by=request.user,
        subject="Stay extension created",
        body=f"Extension booking {extension.booking_id} linked to {booking.booking_id}.",
    )
    return JsonResponse({"extension": _booking_to_dict(extension), "preview": preview}, status=201)


@csrf_exempt
@require_http_methods(["GET"])
def booking_extensions_api(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=403)
    booking = get_object_or_404(StayBooking.objects.select_related("tenant"), pk=booking_id)
    if not user_can_access_tenant(request.user, booking.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    extensions = StayBooking.objects.select_related("tenant", "unit", "commission_record").filter(
        parent_booking=booking
    )
    return JsonResponse(
        {
            "parent_booking": _booking_to_dict(booking),
            "extensions": [_booking_to_dict(row) for row in extensions],
        }
    )


@login_required
@require_permission("billing.settle")
@require_http_methods(["POST"])
def unit_rate_create(request):
    form = StayUnitRateForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Unit rate form is invalid.")
        return redirect("stay-business-dashboard")
    row = form.save()
    log_audit(
        actor=request.user,
        tenant=row.tenant,
        action="stay.rate.updated",
        entity_type="StayUnitRate",
        entity_id=row.id,
        metadata={"unit_id": row.unit_id, "day": row.day.isoformat(), "nightly_rate": str(row.nightly_rate)},
    )
    messages.success(request, "Unit daily rate saved.")
    return redirect("stay-business-dashboard")
