from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from apps.connectors.models import ConnectorEvent, ConnectorHealthLog


class Command(BaseCommand):
    help = "Show connector secret-key version usage for rotation readiness."

    def add_arguments(self, parser):
        parser.add_argument("--hours", type=int, default=24)

    def handle(self, *args, **options):
        hours = max(1, int(options["hours"]))
        since = timezone.now() - timedelta(hours=hours)

        event_rows = (
            ConnectorEvent.objects.filter(received_at__gte=since)
            .values("auth_key_version")
            .annotate(count=Count("id"))
            .order_by("auth_key_version")
        )
        health_rows = (
            ConnectorHealthLog.objects.filter(created_at__gte=since)
            .values("auth_key_version", "is_success")
            .annotate(count=Count("id"))
            .order_by("auth_key_version", "is_success")
        )

        self.stdout.write(f"connector_secret_rotation_status window_hours={hours}")
        self.stdout.write("events_by_key_version:")
        for row in event_rows:
            key = row["auth_key_version"] or "unknown"
            self.stdout.write(f"  {key}: {row['count']}")

        self.stdout.write("health_by_key_version_and_outcome:")
        for row in health_rows:
            key = row["auth_key_version"] or "unknown"
            outcome = "success" if row["is_success"] else "failure"
            self.stdout.write(f"  {key} {outcome}: {row['count']}")

        active_seen = any((row.get("auth_key_version") or "") == "active" for row in event_rows)
        next_seen = any((row.get("auth_key_version") or "") == "next" for row in event_rows)
        self.stdout.write(f"rotation_hint active_seen={active_seen} next_seen={next_seen}")
        if next_seen and not active_seen:
            self.stdout.write(self.style.SUCCESS("Cutover ready: only NEXT key observed in event traffic window."))
        elif active_seen and next_seen:
            self.stdout.write(self.style.WARNING("Dual-key traffic observed: keep grace window until active drops to zero."))
        elif active_seen and not next_seen:
            self.stdout.write(self.style.WARNING("Only ACTIVE key observed: clients may not have switched yet."))
        else:
            self.stdout.write("No connector event traffic in this window.")
