from decimal import Decimal
from django.utils.dateparse import parse_date
from apps.bookings.services import _assert_vehicle_available, BookingError
from apps.fleet.models import Vehicle
from apps.settings_app.models import BusinessProfile

def quote(payload):
    resource = str(payload.get("provider_resource_id") or "")
    vehicle = Vehicle.objects.filter(pk=int(resource)).first() if resource.isdigit() else Vehicle.objects.filter(plate_number=resource).first()
    if not vehicle or vehicle.status in {"MAINTENANCE", "INACTIVE"}:
        raise ValueError("Vehicle is unavailable.")
    start = parse_date(str(payload.get("pickupDate") or payload.get("pickup_date") or ""))
    end = parse_date(str(payload.get("returnDate") or payload.get("return_date") or ""))
    if not start or not end or end <= start or (end-start).days > 366:
        raise ValueError("Choose a valid rental duration of up to 366 days.")
    try: _assert_vehicle_available(vehicle.branch, vehicle, start, end)
    except BookingError as exc: raise ValueError(str(exc)) from exc
    total = (vehicle.daily_rate * (end-start).days).quantize(Decimal("0.001"))
    if total <= 0: raise ValueError("Vehicle rate is not configured.")
    return {"amount": str(total), "currency": BusinessProfile.get_solo().currency_code or "OMR", "quantity": (end-start).days,
        "unit_price": str(vehicle.daily_rate), "tax": "0.000", "policy": {"deposit": str(vehicle.deposit)}}
