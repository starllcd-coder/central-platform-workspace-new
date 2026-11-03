from django.core.management.base import BaseCommand
from django.db.models import Count
from central_sync.models import OutboundEvent

class Command(BaseCommand):
    help = "Inspect queue counts and recent failed event IDs without printing customer payloads."
    def handle(self, *args, **options):
        counts = dict(OutboundEvent.objects.values_list("status").annotate(total=Count("id")))
        self.stdout.write(str(counts))
        for event in OutboundEvent.objects.exclude(last_error="").order_by("-id")[:20]:
            self.stdout.write(f"{event.event_id} {event.status} attempts={event.attempts}: {event.last_error}")
