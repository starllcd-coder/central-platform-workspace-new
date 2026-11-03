from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from central_bridge.client import post_connector

class Command(BaseCommand):
    help = "Send a signed StayLux tenant heartbeat to Central. Reports configured tenant state."
    def add_arguments(self, parser):
        parser.add_argument("--tenant-code", default="")
        parser.add_argument("--kind", choices=["tenant"], default="tenant")
    def handle(self, *args, **options):
        tenant = options["tenant_code"] or settings.CENTRAL_TENANT_CODE
        if not tenant or not settings.CENTRAL_CONNECTOR_SECRET:
            raise CommandError("Configure CENTRAL_TENANT_CODE and CENTRAL_CONNECTOR_SECRET first.")
        result = post_connector("tenant/sync/", {"tenant_code": tenant, "module_code": "staylux", "status": "active"})
        self.stdout.write(self.style.SUCCESS(str(result)))
