from decimal import Decimal
from django.conf import settings
from django.utils.dateparse import parse_date
from inventory.models import Unit
from bookings.models import is_unit_available
from pricing.services import get_applicable_rate_plan, compute_booking_total

def quote(payload):
    resource = str(payload.get("provider_resource_id") or "")
    units = Unit.objects.filter(property_profile_id=getattr(settings,"CENTRAL_PROPERTY_ID",None), is_active=True)
    unit = units.filter(pk=int(resource)).first() if resource.isdigit() else units.filter(code=resource).first()
    if not unit or unit.status in {"maintenance", "housekeeping"}: raise ValueError("Unit is unavailable.")
    start = parse_date(str(payload.get("checkIn") or payload.get("check_in") or ""))
    end = parse_date(str(payload.get("checkOut") or payload.get("check_out") or ""))
    if not start or not end or end <= start or (end-start).days > 366:
        raise ValueError("Choose a valid stay duration of up to 366 nights.")
    guests = int(payload.get("guests") or 1)
    if guests < 1 or guests > unit.guest_capacity: raise ValueError("Guest count exceeds unit capacity.")
    if not is_unit_available(unit.pk, start, end): raise ValueError("Unit is unavailable for these dates.")
    if get_applicable_rate_plan(unit): total, currency = compute_booking_total(unit,start,end)
    else: total, currency = (unit.daily_price or unit.unit_type.base_rate)*(end-start).days, unit.property_profile.currency
    if total <= 0: raise ValueError("Unit rate is not configured.")
    return {"amount": str(total.quantize(Decimal("0.001"))), "currency": currency, "quantity": (end-start).days,
        "unit_price": str((total/(end-start).days).quantize(Decimal("0.000001"))), "tax": "0.000", "policy": {"capacity": unit.guest_capacity}}
