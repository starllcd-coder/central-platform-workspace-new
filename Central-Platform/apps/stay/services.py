from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.billing.models import PaymentTransaction
from apps.billing.services import enrich_and_post_transaction, resolve_commission_rate
from apps.tenants.models import Module, Unit

from .models import (
    StayBooking,
    StayBookingCommission,
    StayBookingPayment,
    StayUnitAvailability,
    StayUnitRate,
)

MONEY_Q = Decimal("0.01")


def _q(value):
    return Decimal(value).quantize(MONEY_Q, rounding=ROUND_HALF_UP)


def _iter_days(start_day, end_day):
    day = start_day
    while day < end_day:
        yield day
        day += timedelta(days=1)


def _staylux_module():
    return Module.objects.filter(code__iexact="STAYLUX").first()


def booking_id(prefix="SB"):
    return f"{prefix}-{timezone.now().strftime('%Y%m%d%H%M%S%f')}"


def unit_is_available(*, unit_id, start_day, end_day, exclude_booking_id=None):
    if end_day <= start_day:
        return False
    overlap = StayBooking.objects.filter(
        unit_id=unit_id,
        status__in=["pending", "confirmed", "checked_in"],
        check_in__lt=end_day,
        check_out__gt=start_day,
    )
    if exclude_booking_id:
        overlap = overlap.exclude(id=exclude_booking_id)
    if overlap.exists():
        return False

    blocked = StayUnitAvailability.objects.filter(
        unit_id=unit_id,
        day__gte=start_day,
        day__lt=end_day,
        status__in=["booked", "held", "out_of_service"],
    )
    if exclude_booking_id:
        blocked = blocked.exclude(booking_id=exclude_booking_id)
    return not blocked.exists()


def suggest_alternative_units(*, booking, start_day, end_day, limit=5):
    qs = Unit.objects.filter(tenant_id=booking.tenant_id, status="active").exclude(id=booking.unit_id)
    if booking.unit.unit_type:
        qs = qs.filter(unit_type=booking.unit.unit_type)
    suggestions = []
    for unit in qs.order_by("name")[:100]:
        if unit_is_available(unit_id=unit.id, start_day=start_day, end_day=end_day):
            suggestions.append(unit)
        if len(suggestions) >= limit:
            break
    return suggestions


def calculate_price_for_unit(*, tenant_id, unit_id, start_day, end_day):
    nightly_rows = StayUnitRate.objects.filter(
        tenant_id=tenant_id,
        unit_id=unit_id,
        day__gte=start_day,
        day__lt=end_day,
    )
    row_map = {row.day: row for row in nightly_rows}
    subtotal = Decimal("0.00")
    currency = "OMR"
    missing_days = []
    for day in _iter_days(start_day, end_day):
        row = row_map.get(day)
        if row is None:
            fallback = (
                StayUnitRate.objects.filter(tenant_id=tenant_id, unit_id=unit_id, day__lte=day)
                .order_by("-day")
                .first()
            )
            if fallback is None:
                missing_days.append(day.isoformat())
                continue
            row = fallback
        subtotal = _q(subtotal + row.nightly_rate)
        currency = row.currency
    if missing_days:
        raise ValueError(f"Missing rate setup for extension days: {', '.join(missing_days[:5])}")
    tax = Decimal("0.00")
    total = _q(subtotal + tax)
    return {"subtotal": subtotal, "tax": tax, "total": total, "currency": currency}


def extension_preview(*, parent_booking, new_check_out):
    if new_check_out <= parent_booking.check_out:
        raise ValueError("new_check_out must be later than current check_out.")
    extension_start = parent_booking.check_out
    extension_end = new_check_out
    same_available = unit_is_available(
        unit_id=parent_booking.unit_id,
        start_day=extension_start,
        end_day=extension_end,
    )
    alternatives = []
    for unit in suggest_alternative_units(
        booking=parent_booking,
        start_day=extension_start,
        end_day=extension_end,
        limit=5,
    ):
        try:
            price = calculate_price_for_unit(
                tenant_id=parent_booking.tenant_id,
                unit_id=unit.id,
                start_day=extension_start,
                end_day=extension_end,
            )
            alternatives.append(
                {
                    "unit_id": unit.id,
                    "unit_code": unit.code,
                    "unit_name": unit.name,
                    "unit_type": unit.unit_type,
                    "price_total": str(price["total"]),
                    "currency": price["currency"],
                }
            )
        except ValueError:
            continue

    selected_unit_id = parent_booking.unit_id if same_available else (alternatives[0]["unit_id"] if alternatives else None)
    selected_price = None
    if selected_unit_id:
        selected_price = calculate_price_for_unit(
            tenant_id=parent_booking.tenant_id,
            unit_id=selected_unit_id,
            start_day=extension_start,
            end_day=extension_end,
        )

    return {
        "parent_booking_id": parent_booking.id,
        "extension_start": extension_start,
        "extension_end": extension_end,
        "same_unit_available": same_available,
        "same_unit_id": parent_booking.unit_id,
        "suggested_unit_id": selected_unit_id if not same_available else None,
        "alternatives": alternatives,
        "price": {
            "subtotal": str(selected_price["subtotal"]) if selected_price else "0.00",
            "tax": str(selected_price["tax"]) if selected_price else "0.00",
            "total": str(selected_price["total"]) if selected_price else "0.00",
            "currency": selected_price["currency"] if selected_price else parent_booking.currency,
        },
    }


def _commission_for_booking(booking, total_amount):
    module = booking.module or _staylux_module()
    rate = resolve_commission_rate(
        tenant_id=booking.tenant_id,
        module_id=module.id if module else None,
        booking_type="online",
        effective_date=timezone.localdate(),
    )
    amount = _q((total_amount * Decimal(rate or 0)) / Decimal("100"))
    return _q(rate or 0), amount


def _apply_availability(booking):
    for day in _iter_days(booking.check_in, booking.check_out):
        StayUnitAvailability.objects.update_or_create(
            tenant_id=booking.tenant_id,
            unit_id=booking.unit_id,
            day=day,
            defaults={"status": "booked", "booking": booking},
        )


@transaction.atomic
def create_stay_booking(*, tenant, unit, check_in, check_out, payment_rule, customer_name="", customer_email="", customer_phone="", guests=1, notes="", created_by=None):
    if not unit_is_available(unit_id=unit.id, start_day=check_in, end_day=check_out):
        raise ValueError("Selected unit is not available for requested dates.")
    price = calculate_price_for_unit(
        tenant_id=tenant.id,
        unit_id=unit.id,
        start_day=check_in,
        end_day=check_out,
    )
    module = _staylux_module()
    booking = StayBooking.objects.create(
        tenant=tenant,
        module=module,
        unit=unit,
        booking_id=booking_id("SB"),
        booking_type="original",
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        payment_rule=payment_rule,
        payment_status="unpaid",
        currency=price["currency"],
        subtotal_amount=price["subtotal"],
        tax_amount=price["tax"],
        total_amount=price["total"],
        notes=notes,
        created_by=created_by,
        status="confirmed",
    )
    commission_rate, commission_amount = _commission_for_booking(booking, booking.total_amount)
    StayBookingCommission.objects.create(
        booking=booking,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
        currency=booking.currency,
        status="accrued",
    )
    payment = StayBookingPayment.objects.create(
        booking=booking,
        amount_due=booking.total_amount,
        amount_paid=Decimal("0.00"),
        billing_reference="",
    )

    if payment_rule == "pay_now":
        tx = PaymentTransaction.objects.create(
            tenant=tenant,
            module=module,
            booking_ref=booking.booking_id,
            currency=booking.currency,
            payment_channel="online",
            status="paid",
            lifecycle_state="posted",
            settlement_state="pending",
            booking_type="online",
            gross_amount=booking.total_amount,
            gateway_fee=Decimal("0.00"),
            tax_amount=booking.tax_amount,
            occurred_at=timezone.now(),
            metadata={"stay_booking_id": booking.id, "booking_type": booking.booking_type},
        )
        enrich_and_post_transaction(tx)
        booking.payment_status = "paid"
        booking.save(update_fields=["payment_status", "updated_at"])
        payment.amount_paid = booking.total_amount
        payment.payment_transaction = tx
        payment.billing_reference = tx.booking_ref
        payment.save(update_fields=["amount_paid", "payment_transaction", "billing_reference"])
    elif payment_rule == "pay_at_property":
        booking.payment_status = "due_at_property"
        booking.save(update_fields=["payment_status", "updated_at"])
    elif payment_rule == "add_to_existing_bill":
        booking.payment_status = "added_to_bill"
        booking.save(update_fields=["payment_status", "updated_at"])

    _apply_availability(booking)
    return booking


@transaction.atomic
def extend_stay_booking(*, parent_booking, new_check_out, payment_rule, selected_unit_id=None, notes="", created_by=None):
    preview = extension_preview(parent_booking=parent_booking, new_check_out=new_check_out)
    extension_start = parent_booking.check_out
    extension_end = new_check_out

    if selected_unit_id:
        unit = Unit.objects.filter(id=selected_unit_id, tenant_id=parent_booking.tenant_id).first()
        if unit is None:
            raise ValueError("Selected extension unit not found in tenant.")
    elif preview["same_unit_available"]:
        unit = parent_booking.unit
    elif preview["alternatives"]:
        unit = Unit.objects.get(id=preview["alternatives"][0]["unit_id"])
    else:
        raise ValueError("No available unit found for requested extension dates.")

    if not unit_is_available(unit_id=unit.id, start_day=extension_start, end_day=extension_end):
        raise ValueError("Selected extension unit is no longer available.")

    price = calculate_price_for_unit(
        tenant_id=parent_booking.tenant_id,
        unit_id=unit.id,
        start_day=extension_start,
        end_day=extension_end,
    )
    extension = StayBooking.objects.create(
        tenant=parent_booking.tenant,
        module=parent_booking.module or _staylux_module(),
        unit=unit,
        booking_id=booking_id("SE"),
        booking_type="extension",
        parent_booking=parent_booking,
        billed_to_booking=parent_booking if payment_rule == "add_to_existing_bill" else None,
        customer_name=parent_booking.customer_name,
        customer_email=parent_booking.customer_email,
        customer_phone=parent_booking.customer_phone,
        check_in=extension_start,
        check_out=extension_end,
        guests=parent_booking.guests,
        status="confirmed",
        payment_rule=payment_rule,
        payment_status="unpaid",
        currency=price["currency"],
        subtotal_amount=price["subtotal"],
        tax_amount=price["tax"],
        total_amount=price["total"],
        notes=notes,
        created_by=created_by,
    )

    commission_rate, commission_amount = _commission_for_booking(extension, extension.total_amount)
    StayBookingCommission.objects.create(
        booking=extension,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
        currency=extension.currency,
        status="accrued",
    )
    payment = StayBookingPayment.objects.create(
        booking=extension,
        amount_due=extension.total_amount,
        amount_paid=Decimal("0.00"),
        billing_reference=parent_booking.booking_id if payment_rule == "add_to_existing_bill" else "",
    )
    if payment_rule == "pay_now":
        tx = PaymentTransaction.objects.create(
            tenant=extension.tenant,
            module=extension.module,
            booking_ref=extension.booking_id,
            currency=extension.currency,
            payment_channel="online",
            status="paid",
            lifecycle_state="posted",
            settlement_state="pending",
            booking_type="online",
            gross_amount=extension.total_amount,
            gateway_fee=Decimal("0.00"),
            tax_amount=extension.tax_amount,
            occurred_at=timezone.now(),
            metadata={
                "stay_booking_id": extension.id,
                "parent_booking_id": parent_booking.id,
                "booking_type": "extension",
            },
        )
        enrich_and_post_transaction(tx)
        extension.payment_status = "paid"
        extension.save(update_fields=["payment_status", "updated_at"])
        payment.amount_paid = extension.total_amount
        payment.payment_transaction = tx
        payment.billing_reference = tx.booking_ref
        payment.save(update_fields=["amount_paid", "payment_transaction", "billing_reference"])
    elif payment_rule == "pay_at_property":
        extension.payment_status = "due_at_property"
        extension.save(update_fields=["payment_status", "updated_at"])
    elif payment_rule == "add_to_existing_bill":
        extension.payment_status = "added_to_bill"
        extension.save(update_fields=["payment_status", "updated_at"])

    _apply_availability(extension)
    return extension, preview
