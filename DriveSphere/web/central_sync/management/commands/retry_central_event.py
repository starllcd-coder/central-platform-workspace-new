from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from central_sync.models import OutboundEvent

class Command(BaseCommand):
    help = "Requeue one inspected dead event, preserving its idempotency identity."
    def add_arguments(self, parser):
        parser.add_argument("event_id")
    def handle(self, *args, **options):
        from uuid import UUID
        try:
            event_id = UUID(options["event_id"])
        except ValueError:
            raise CommandError("A valid event UUID is required.")
        changed = OutboundEvent.objects.filter(event_id=event_id, status="dead").update(status="pending", attempts=0, lease_token="", next_attempt_at=timezone.now())
        if not changed:
            raise CommandError("No dead event matches that ID.")
        self.stdout.write("Event requeued with its original identity.")
