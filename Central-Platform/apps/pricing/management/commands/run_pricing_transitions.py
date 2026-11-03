from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.pricing.services import apply_due_pricing_transitions


class Command(BaseCommand):
    help = "Apply scheduled pricing transitions with effective_on <= run date."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--run-date", type=str, default="")

    def handle(self, *args, **options):
        limit = max(1, int(options["limit"]))
        run_date_text = (options.get("run_date") or "").strip()
        if run_date_text:
            try:
                run_date = timezone.datetime.strptime(run_date_text, "%Y-%m-%d").date()
            except ValueError as exc:
                raise ValueError("--run-date must be YYYY-MM-DD") from exc
        else:
            run_date = timezone.localdate()

        result = apply_due_pricing_transitions(run_date=run_date, limit=limit)
        self.stdout.write(
            "run_pricing_transitions "
            f"date={run_date.isoformat()} considered={result['considered']} "
            f"applied={result['applied']} failed={result['failed']}"
        )
