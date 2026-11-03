from decimal import Decimal
from django.utils.dateparse import parse_date
from apps.bookings.services import create_booking as create_rental, BookingError
from apps.customers.models import Customer
from apps.fleet.models import Vehicle
from apps.settings_app.models import BusinessProfile

def create_booking(envelope, amount):
    payload = envelope["payload"]
    resource = str(envelope.get("provider_resource_id") or "")
    # Numeric IDs are primary keys; other IDs must be exact plate numbers.
    vehicles = Vehicle.objects.select_for_update()
    vehicle = vehicles.filter(pk=int(resource)).first() if resource.isdigit() else vehicles.filter(plate_number=resource).first()
    if not vehicle or vehicle.status in {"MAINTENANCE", "INACTIVE"}:
        raise ValueError("Requested vehicle is unavailable.")
    pickup = parse_date(str(payload.get("pickupDate") or payload.get("pickup_date") or ""))
    end = parse_date(str(payload.get("returnDate") or payload.get("return_date") or ""))
    if not pickup or not end or end <= pickup:
        raise ValueError("Valid pickup and return dates are required.")
    business = BusinessProfile.get_solo()
    if envelope.get("currency") != (business.currency_code or "OMR"):
        raise ValueError("Booking currency does not match provider currency.")
    # Provider rates are authoritative; reject stale Central listings.
    from .quotes import quote
    expected = Decimal(quote({**payload, "provider_resource_id": resource})["amount"])
    if amount != expected or expected <= 0:
        raise ValueError("Provider price changed; refresh the marketplace quote.")
    name = str(payload.get("fullName") or payload.get("customer_name") or "").strip()
    email = str(payload.get("email") or payload.get("customer_email") or "").strip()
    if not name or not email:
        raise ValueError("Customer name and email are required.")
    customer = Customer.objects.create(name=name, email=email, phone_number=str(payload.get("phone") or ""), license_number=str(payload.get("driverLicenseNumber") or ""))
    try:
        booking = create_rental(branch=vehicle.branch, created_by=None, customer=customer, vehicle=vehicle,
            pickup_date=pickup, return_date=end, daily_rate=vehicle.daily_rate, vat_rate=0,
            notes=f"Central marketplace {envelope['booking_id']}")
    except BookingError as exc:
        raise ValueError(str(exc)) from exc
    booking.pickup_location = str(payload.get("pickupLocation") or "")
    booking.return_location = str(payload.get("returnLocation") or "")
    booking.save(update_fields=["pickup_location", "return_location"])
    return booking
