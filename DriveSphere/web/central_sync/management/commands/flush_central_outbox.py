import time
import uuid
from central_sync.client import post_connector
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from central_sync.worker import flush

class Command(BaseCommand):
    help = "Deliver queued Central status events; network calls never run inside booking requests."
    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--watch", action="store_true")
        parser.add_argument("--interval", type=int, default=30)
    def handle(self, *args, **options):
        if options["limit"] < 1 or options["interval"] < 5:
            raise CommandError("Use a positive limit and an interval of at least 5 seconds.")
        if not (getattr(settings, "CENTRAL_SYNC_ENABLED", False) and settings.CENTRAL_TENANT_CODE
                and settings.CENTRAL_CONNECTOR_SECRET and settings.CENTRAL_CONNECTOR_SIGNED):
            raise CommandError("Enable CENTRAL_SYNC_ENABLED and configure tenant, secret and signed connector requests.")
        last_heartbeat = 0
        try:
            while True:
                if options["watch"] and time.monotonic()-last_heartbeat > 300:
                    try:
                        post_connector("webhooks/events/", {"event_name":"connector.heartbeat","external_event_id":uuid.uuid4().hex,
                            "tenant_code":settings.CENTRAL_TENANT_CODE,"module_code":settings.CENTRAL_MODULE_CODE})
                    except Exception:
                        self.stderr.write("Central heartbeat failed; queued deliveries remain available for retry.")
                    last_heartbeat=time.monotonic()
                self.stdout.write(str(flush(options["limit"])))
                if not options["watch"]:
                    break
                time.sleep(options["interval"])
        except KeyboardInterrupt:
            pass
