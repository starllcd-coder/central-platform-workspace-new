import uuid
from django.conf import settings
from django.db.models.signals import post_delete
from django.utils import timezone
from .models import OutboundEvent
from .resources import snapshots

def queue_resource(sender, instance, raw=False, signal=None, **kwargs):
    if raw or not getattr(settings, "CENTRAL_SYNC_ENABLED", False):
        return
    deleted = signal is post_delete
    for data in snapshots(instance, deleted=deleted):
        event = OutboundEvent(payload={})
        event.payload = {"tenant_code": settings.CENTRAL_TENANT_CODE, "module_code": settings.CENTRAL_MODULE_CODE,
            "event_name": "marketplace.resource.updated", "external_event_id": str(event.event_id), "data": data}
        event.save()

def queue_related(sender, instance, raw=False, **kwargs):
    if raw or not getattr(settings, "CENTRAL_SYNC_ENABLED", False):
        return
    from .resources import related_resources
    for resource in related_resources(instance):
        queue_resource(type(resource), resource)
