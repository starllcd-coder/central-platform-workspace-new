from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from central_sync.inventory import queue_resource
from apps.catalog.models import ItemServicePrice as Resource

class Command(BaseCommand):
    help = "Queue a complete current resource inventory for initial sync or reconciliation."
    def handle(self, *args, **options):
        if not settings.CENTRAL_SYNC_ENABLED:
            raise CommandError("Enable CENTRAL_SYNC_ENABLED after applying migrations.")
        count = 0
        for resource in Resource.objects.all().iterator():
            queue_resource(Resource, resource)
            count += 1
        self.stdout.write(f"Scanned {count} resources; run flush_central_outbox to deliver snapshots.")
