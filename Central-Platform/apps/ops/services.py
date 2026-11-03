import json
from datetime import timedelta
from urllib import request as urllib_request
from urllib.error import URLError

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from .models import AuditLog, NotificationEvent, NotificationTemplate


def log_audit(*, actor=None, tenant=None, module=None, action="", entity_type="", entity_id="", metadata=None):
    return AuditLog.objects.create(
        actor=actor,
        tenant=tenant,
        module=module,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id or ""),
        metadata=metadata or {},
    )


def _render_template(text, context):
    if not text:
        return ""
    ctx = context or {}
    try:
        return text.format(**ctx)
    except Exception:
        return text


def _send_email(event: NotificationEvent):
    if not event.recipient:
        raise ValueError("Email recipient is required.")
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@central.local")
    send_mail(
        subject=event.subject or "Notification",
        message=event.body,
        from_email=from_email,
        recipient_list=[event.recipient],
        fail_silently=False,
    )
    return "email-ok"


def _send_webhook(event: NotificationEvent):
    if not event.recipient:
        raise ValueError("Webhook URL is required in recipient.")
    payload = {
        "subject": event.subject,
        "body": event.body,
        "context": event.context,
        "tenant_id": event.tenant_id,
        "module_id": event.module_id,
    }
    req = urllib_request.Request(
        event.recipient,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    timeout = int(getattr(settings, "NOTIFICATION_WEBHOOK_TIMEOUT", 6))
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        code = getattr(resp, "status", 200)
    if code >= 400:
        raise URLError(f"Webhook returned status {code}")
    return f"webhook-{code}"


def _send_sms(event: NotificationEvent):
    provider = getattr(settings, "SMS_PROVIDER", "").strip().lower()
    if provider == "mock" and settings.DEBUG:
        return "sms-mock"
    raise ValueError("SMS provider is not configured.")


def dispatch_notification(event: NotificationEvent):
    try:
        if event.channel == "in_app":
            external_id = "in-app"
        elif event.channel == "email":
            external_id = _send_email(event)
        elif event.channel == "webhook":
            external_id = _send_webhook(event)
        elif event.channel == "sms":
            external_id = _send_sms(event)
        else:
            raise ValueError("Unsupported notification channel.")

        event.status = "sent"
        event.attempts += 1
        event.last_error = ""
        event.external_id = external_id
        event.sent_at = timezone.now()
        event.next_attempt_at = None
        event.save(
            update_fields=[
                "status",
                "attempts",
                "last_error",
                "external_id",
                "sent_at",
                "next_attempt_at",
            ]
        )
        return True
    except Exception as exc:
        event.status = "failed"
        event.attempts += 1
        event.last_error = str(exc)[:255]
        if event.attempts < event.max_attempts:
            delay_minutes = 2 * event.attempts
            event.next_attempt_at = timezone.now() + timedelta(minutes=delay_minutes)
        event.save(update_fields=["status", "attempts", "last_error", "next_attempt_at"])
        return False


def queue_notification(
    *,
    template_code=None,
    channel="in_app",
    recipient="",
    tenant=None,
    module=None,
    triggered_by=None,
    subject="",
    body="",
    context=None,
):
    template = None
    if template_code:
        template = NotificationTemplate.objects.filter(code=template_code, is_active=True).first()

    final_channel = template.channel if template else channel
    final_subject = _render_template(template.subject_template, context) if template else subject
    final_body = _render_template(template.body_template, context) if template else body
    if not final_body:
        final_body = body or "Notification event"

    event = NotificationEvent.objects.create(
        template=template,
        tenant=tenant,
        module=module,
        triggered_by=triggered_by,
        channel=final_channel,
        recipient=recipient,
        subject=final_subject,
        body=final_body,
        context=context or {},
        status="pending",
        next_attempt_at=timezone.now(),
    )
    dispatch_notification(event)
    return event


def process_pending_notifications(limit=100):
    now = timezone.now()
    qs = NotificationEvent.objects.filter(
        status__in=["pending", "failed"],
        attempts__lt=models.F("max_attempts"),
    ).filter(models.Q(next_attempt_at__isnull=True) | models.Q(next_attempt_at__lte=now))
    processed = 0
    for event in qs.order_by("created_at")[:limit]:
        dispatch_notification(event)
        processed += 1
    return processed
