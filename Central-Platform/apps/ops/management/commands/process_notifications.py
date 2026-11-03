from django.core.management.base import BaseCommand

from apps.ops.services import process_pending_notifications


class Command(BaseCommand):
    help = "Process pending/failed notification events."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        limit = options["limit"]
        count = process_pending_notifications(limit=limit)
        self.stdout.write(self.style.SUCCESS(f"Processed {count} notification events."))
