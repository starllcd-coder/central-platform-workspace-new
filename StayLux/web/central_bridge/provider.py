from decimal import Decimal
from django.conf import settings
from django.utils.dateparse import parse_date
from bookings.models import Booking, is_unit_available
from guests.models import Guest
from inventory.models import Unit

def create_booking(envelope, amount):
    payload = envelope["payload"]
    resource = str(envelope.get("provider_resource_id") or "")
    # Explicit property binding prevents cross-property bookings in a shared backend.
    property_id = getattr(settings, "CENTRAL_PROPERTY_ID", "")
    if not property_id:
        raise ValueError("CENTRAL_PROPERTY_ID must identify the tenant property.")
    units = Unit.objects.select_for_update().filter(property_profile_id=property_id, is_active=True)
    unit = units.filter(pk=int(resource)).first() if resource.isdigit() else units.filter(code=resource).first()
    if not unit or unit.status in {"maintenance", "housekeeping"}:
        raise ValueError("Requested unit is unavailable.")
    start = parse_date(str(payload.get("checkIn") or payload.get("check_in") or ""))
    end = parse_date(str(payload.get("checkOut") or payload.get("check_out") or ""))
    if not start or not end or end <= start:
        raise ValueError("Valid check-in and check-out dates are required.")
    adults = int(payload.get("guests") or 1)
    if adults < 1 or adults > unit.guest_capacity:
        raise ValueError("Guest count exceeds unit capacity.")
    if not is_unit_available(unit.pk, start, end):
        raise ValueError("Unit is not available for these dates.")
    if envelope.get("currency") != unit.property_profile.currency:
        raise ValueError("Booking currency does not match provider currency.")
    from .quotes import quote
    expected = Decimal(quote({**payload, "provider_resource_id": resource})["amount"])
    if expected <= 0 or amount != expected:
        raise ValueError("Provider price changed; refresh the marketplace quote.")
    name = str(payload.get("fullName") or payload.get("customer_name") or "").strip()
    email = str(payload.get("email") or payload.get("customer_email") or "").strip()
    if not name or not email:
        raise ValueError("Customer name and email are required.")
    guest = Guest.objects.create(property_profile=unit.property_profile, full_name=name, email=email,
        phone=str(payload.get("phone") or ""))
    booking = Booking(property_profile=unit.property_profile, unit=unit, guest=guest,
        start_date=start, end_date=end, adults=adults, rate=(amount / (end-start).days).quantize(Decimal("0.001")),
        notes=f"Central marketplace {envelope['booking_id']}")
    booking.full_clean()
    booking.lock_pricing()
    booking.locked_total = amount
    booking.save()
    return booking
