from celery import shared_task
from django.core.management import call_command


@shared_task(name="apps.connectors.tasks.prune_connector_nonces_task")
def prune_connector_nonces_task(days=None, limit=5000, dry_run=False):
    kwargs = {"limit": int(limit), "dry_run": bool(dry_run)}
    if days is not None:
        kwargs["days"] = int(days)
    call_command("prune_connector_nonces", **kwargs)
    return {"ok": True, **kwargs}


@shared_task(name="apps.connectors.tasks.dispatch_marketplace_bookings_task")
def dispatch_marketplace_bookings_task(limit=100):
    call_command("dispatch_marketplace_bookings", limit=int(limit))
    return {"ok": True, "limit": int(limit)}


@shared_task(name="apps.connectors.tasks.dispatch_payment_updates_task")
def dispatch_payment_updates_task():
    call_command("dispatch_payment_updates",limit=100)
