from celery import shared_task
from django.core.management import call_command


@shared_task(name="apps.ops.tasks.process_notifications_task")
def process_notifications_task(limit=100):
    call_command("process_notifications", limit=int(limit))
    return {"ok": True, "limit": int(limit)}


@shared_task(name="apps.ops.tasks.monitor_platform_health_task")
def monitor_platform_health_task(window_minutes=None, dry_run=False):
    kwargs = {"dry_run": bool(dry_run)}
    if window_minutes is not None:
        kwargs["window_minutes"] = int(window_minutes)
    call_command("monitor_platform_health", **kwargs)
    return {"ok": True, **kwargs}
