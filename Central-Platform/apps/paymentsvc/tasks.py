from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import PaymentRequestNonce


@shared_task(name="apps.paymentsvc.tasks.prune_payment_nonces_task")
def prune_payment_nonces_task():
    retention_days = int(getattr(settings, "PAYMENT_NONCE_RETENTION_DAYS", 7))
    cutoff = timezone.now() - timedelta(days=max(1, retention_days))
    deleted, _ = PaymentRequestNonce.objects.filter(created_at__lt=cutoff).delete()
    return {"deleted": deleted, "retention_days": retention_days}


@shared_task(name="apps.paymentsvc.tasks.reconcile_gateway_payments_task")
def reconcile_gateway_payments_task():
    from django.core.management import call_command
    call_command("reconcile_gateway_payments",limit=100)
