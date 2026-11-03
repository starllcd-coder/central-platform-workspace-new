from django.conf import settings
from django.db.models.signals import post_delete
from django.utils import timezone
from .models import OutboundEvent
from .provider import external_id, mapped_status

def queue_status(sender, instance, raw=False, signal=None, **kwargs):
    # Disabled integrations must not affect ordinary app saves or old databases.
    if raw or not getattr(settings, "CENTRAL_SYNC_ENABLED", False):
        return
    update_fields = kwargs.get("update_fields")
    if signal is not post_delete and update_fields is not None and "status" not in update_fields:
        return
    booking_id = external_id(instance)
    status = "cancelled" if signal is post_delete else mapped_status(instance.status)
    if not booking_id or not status:
        return
    event = OutboundEvent(payload={})
    event.payload = {
        "tenant_code": settings.CENTRAL_TENANT_CODE,
        "module_code": settings.CENTRAL_MODULE_CODE,
        "event_name": "marketplace.booking.updated",
        "external_event_id": str(event.event_id),
        "data": {"booking_id": booking_id, "status": status,
            "updated_at": (timezone.now() if signal is post_delete else instance.updated_at).isoformat()},
    }
    # Participates in the originating transaction when the caller uses atomic().
    # No network, price, booking, inventory, or UI changes are made here.
    event.save()
