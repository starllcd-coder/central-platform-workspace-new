from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.connectors.models import ConnectorHealthLog
from apps.ops.models import NotificationEvent
from apps.ops.services import queue_notification


class Command(BaseCommand):
    help = "Evaluate platform health and emit alert notifications when thresholds are breached."

    def add_arguments(self, parser):
        parser.add_argument("--window-minutes", type=int, default=None)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        window_minutes = options["window_minutes"]
        if window_minutes is None:
            window_minutes = int(getattr(settings, "OPS_ALERT_WINDOW_MINUTES", 15))
        window_minutes = max(1, int(window_minutes))
        dry_run = bool(options["dry_run"])

        now = timezone.now()
        since = now - timedelta(minutes=window_minutes)
        max_failed_notifications = int(getattr(settings, "OPS_ALERT_MAX_FAILED_NOTIFICATIONS", 10))
        max_connector_failures = int(getattr(settings, "OPS_ALERT_MAX_CONNECTOR_FAILURES", 20))

        failed_notifications = NotificationEvent.objects.filter(
            status="failed",
            created_at__gte=since,
        ).count()
        connector_failures = ConnectorHealthLog.objects.filter(
            is_success=False,
            created_at__gte=since,
        ).count()

        breaches = []
        if failed_notifications >= max_failed_notifications:
            breaches.append(f"failed_notifications={failed_notifications}>={max_failed_notifications}")
        if connector_failures >= max_connector_failures:
            breaches.append(f"connector_failures={connector_failures}>={max_connector_failures}")

        alert_sent = False
        alert_key = f"ops_health_alert:{since.strftime('%Y%m%d%H')}"
        if breaches and not dry_run:
            # Reduce alert noise: one alert per rolling hour window.
            if cache.add(alert_key, 1, timeout=3600):
                body = (
                    "Platform health alert triggered.\n"
                    f"Window minutes: {window_minutes}\n"
                    f"Failed notifications: {failed_notifications}\n"
                    f"Connector failures: {connector_failures}\n"
                    f"Breaches: {', '.join(breaches)}"
                )
                queue_notification(
                    channel="in_app",
                    recipient="ops",
                    subject="Platform Health Alert",
                    body=body,
                    context={
                        "window_minutes": window_minutes,
                        "failed_notifications": failed_notifications,
                        "connector_failures": connector_failures,
                    },
                )
                alert_email = str(getattr(settings, "OPS_ALERT_EMAIL", "") or "").strip()
                if alert_email:
                    queue_notification(
                        channel="email",
                        recipient=alert_email,
                        subject="Platform Health Alert",
                        body=body,
                        context={},
                    )
                alert_sent = True

        self.stdout.write(
            f"monitor_platform_health dry_run={dry_run} window_minutes={window_minutes} "
            f"failed_notifications={failed_notifications} connector_failures={connector_failures} "
            f"breaches={len(breaches)} alert_sent={alert_sent}"
        )
