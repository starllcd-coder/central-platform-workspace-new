from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from apps.marketplace.models import MarketplaceBooking

EVENT_NAME = "marketplace.booking.updated"

def apply_provider_update(payload, tenant, module):
    """Called within the same transaction as the inbound connector event log."""
    if payload.get("event_name") != EVENT_NAME:
        return
    if not tenant or not module:
        raise ValueError("A known tenant and module are required for booking updates.")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("Booking update data must be an object.")
    status = data.get("status")
    if status not in {"pending", "confirmed", "completed", "cancelled"}:
        raise ValueError("Unsupported booking lifecycle status.")
    try:
        updated = parse_datetime(str(data.get("updated_at") or ""))
    except ValueError:
        updated = None
    if not updated or timezone.is_naive(updated) or updated > timezone.now() + timedelta(minutes=5):
        raise ValueError("A valid timezone-aware provider timestamp is required.")
    booking = MarketplaceBooking.objects.select_for_update().filter(
        booking_id=str(data.get("booking_id") or ""), tenant=tenant, module=module).first()
    if booking is None:
        raise ValueError("Booking not found for this tenant and module.")
    if booking.provider_updated_at and updated <= booking.provider_updated_at:
        return
    # A delayed intermediate event must not resurrect a finished/cancelled booking.
    if booking.status in {"completed", "cancelled"} and status != booking.status:
        return
    booking.status = status
    booking.provider_updated_at = updated
    if status in {"confirmed", "completed"}:
        booking.fulfillment_status = "provider_confirmed"
    booking.save(update_fields=["status", "fulfillment_status", "provider_updated_at", "updated_at"])
