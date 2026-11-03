import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.ops.services import process_pending_notifications


class Command(BaseCommand):
    help = "Run ops worker loop to process notification retries."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Run a single cycle and exit.")
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument(
            "--interval",
            type=int,
            default=int(getattr(settings, "OPS_WORKER_INTERVAL_SECONDS", 30)),
            help="Seconds between cycles in loop mode.",
        )

    def _run_cycle(self, limit):
        processed = process_pending_notifications(limit=limit)
        self.stdout.write(
            f"[{timezone.localtime().isoformat(timespec='seconds')}] "
            f"processed_notifications={processed}"
        )
        return processed

    def handle(self, *args, **options):
        limit = options["limit"]
        once = options["once"]
        interval = max(5, int(options["interval"]))

        if once:
            self._run_cycle(limit=limit)
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Ops worker started (interval={interval}s, limit={limit}). Press Ctrl+C to stop."
            )
        )
        try:
            while True:
                self._run_cycle(limit=limit)
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Ops worker stopped."))
