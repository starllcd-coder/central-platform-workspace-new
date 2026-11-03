import uuid
from datetime import timedelta
from django.db.models import F
from django.utils import timezone
from .client import post_connector
from .models import OutboundEvent

def flush(limit=100):
    now = timezone.now()
    candidates = list(OutboundEvent.objects.filter(status__in=["pending", "sending"],
        next_attempt_at__lte=now).order_by("id").values_list("pk", flat=True)[:limit])
    counts = {"delivered": 0, "failed": 0}
    for pk in candidates:
        token = uuid.uuid4().hex
        claimed = OutboundEvent.objects.filter(pk=pk, status__in=["pending", "sending"],
            next_attempt_at__lte=now).update(status="sending", lease_token=token,
                next_attempt_at=now + timedelta(minutes=5), attempts=F("attempts") + 1)
        if not claimed:
            continue
        event = OutboundEvent.objects.get(pk=pk)
        try:
            response = post_connector("webhooks/events/", event.payload)
            if response.get("accepted") is not True:
                raise ValueError("Central did not acknowledge the event.")
            OutboundEvent.objects.filter(pk=pk, lease_token=token).update(
                status="delivered", delivered_at=timezone.now(), last_error="", lease_token="")
            counts["delivered"] += 1
        except Exception as exc:
            exhausted = event.attempts >= 8
            OutboundEvent.objects.filter(pk=pk, lease_token=token).update(
                status="dead" if exhausted else "pending", last_error=str(exc)[:500], lease_token="",
                next_attempt_at=timezone.now() + timedelta(seconds=min(60 * 2 ** min(event.attempts - 1, 6), 3600)))
            counts["failed"] += 1
    return counts
