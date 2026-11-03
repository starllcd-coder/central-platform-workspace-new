from datetime import timedelta
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from central_sync.models import OutboundEvent

class Command(BaseCommand):
    help = "Prune delivered sync events older than 30 days and expired bridge nonces. Never prune pending/dead events or booking receipts."
    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--limit", type=int, default=1000)
        parser.add_argument("--dry-run", action="store_true")
    def handle(self, *args, **options):
        if options["days"] < 1 or options["limit"] < 1:
            raise CommandError("days and limit must be positive.")
        cutoff = timezone.now() - timedelta(days=options["days"])
        ids = list(OutboundEvent.objects.filter(status="delivered", delivered_at__lt=cutoff).values_list("pk", flat=True)[:options["limit"]])
        self.stdout.write(f"Delivered events eligible: {len(ids)}")
        if not options["dry_run"]:
            OutboundEvent.objects.filter(pk__in=ids, status="delivered").delete()
        if apps.is_installed("central_bridge"):
            nonce_model = apps.get_model("central_bridge", "RequestNonce")
            ids = list(nonce_model.objects.filter(created_at__lt=timezone.now()-timedelta(days=1)).values_list("pk", flat=True)[:options["limit"]])
            self.stdout.write(f"Expired nonces eligible: {len(ids)}")
            if not options["dry_run"]:
                nonce_model.objects.filter(pk__in=ids).delete()
