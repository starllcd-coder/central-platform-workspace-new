from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.connectors.models import ConnectorRequestNonce


class Command(BaseCommand):
    help = "Prune old connector request nonces used for replay protection."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=None)
        parser.add_argument("--limit", type=int, default=5000)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        days = options["days"]
        if days is None:
            days = int(getattr(settings, "CONNECTOR_NONCE_RETENTION_DAYS", 7))
        days = max(1, int(days))
        limit = max(1, int(options["limit"]))
        dry_run = bool(options["dry_run"])

        cutoff = timezone.now() - timedelta(days=days)
        qs = ConnectorRequestNonce.objects.filter(created_at__lt=cutoff).order_by("id")
        ids = list(qs.values_list("id", flat=True)[:limit])
        deleted = 0
        if ids and not dry_run:
            deleted, _ = ConnectorRequestNonce.objects.filter(id__in=ids).delete()

        self.stdout.write(
            f"prune_connector_nonces dry_run={dry_run} retention_days={days} considered={len(ids)} deleted={deleted}"
        )
