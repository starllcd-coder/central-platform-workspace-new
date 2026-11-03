from celery import shared_task
from django.core.management import call_command


@shared_task(name="apps.pricing.tasks.reconcile_subscriptions_task")
def reconcile_subscriptions_task(limit=500, dry_run=False):
    call_command("reconcile_subscriptions", limit=int(limit), dry_run=bool(dry_run))
    return {"ok": True, "limit": int(limit), "dry_run": bool(dry_run)}
