import json
import hashlib
import hmac
import os
import time
import uuid
from datetime import timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.connectors.models import AppConnector, ConnectorEvent
from apps.marketplace.models import MarketplaceBooking


DEFAULT_ENDPOINTS = {
    "staylux": "/api/central/bookings/",
    "drivesphere": "/api/central/bookings/",
    "laundrex": "/orders/central/webhook/",
}


class Command(BaseCommand):
    help = "Dispatch queued Nexivo marketplace bookings from Central to provider apps."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        limit = int(options["limit"])
        dry_run = bool(options["dry_run"])
        processed = 0
        dispatched = 0
        failed = 0

        bookings = (
            MarketplaceBooking.objects.select_related("module", "tenant", "connector_event")
            .filter(
                fulfillment_status__in=["connector_queued", "central_confirmed"],
                status__in=["pending", "confirmed"],
                tenant__account_type="production",
                connector_event__isnull=False,
                connector_event__status__in=["accepted", "dispatch_failed", "dispatching"],
            )
            .filter(Q(connector_event__next_retry_at__isnull=True) | Q(connector_event__next_retry_at__lte=timezone.now()))
            .order_by("created_at")[:limit]
        )

        for booking in bookings:
            processed += 1
            event = booking.connector_event
            module_code = booking.module.code
            target_url = self._target_url(booking)
            if not target_url:
                self._mark_failed(booking, event, f"No connector URL configured for {module_code}.", dry_run)
                failed += 1
                continue

            if dry_run:
                self.stdout.write(f"Would dispatch {booking.booking_id} to {target_url}")
                continue

            claimed = ConnectorEvent.objects.filter(
                pk=event.pk,
                status__in=["accepted", "dispatch_failed", "dispatching"],
            ).filter(
                Q(next_retry_at__isnull=True) | Q(next_retry_at__lte=timezone.now())
            ).update(status="dispatching", next_retry_at=timezone.now() + timedelta(minutes=5))
            if not claimed:
                continue
            event.refresh_from_db()

            ok, detail = self._post_event(target_url, event)
            if ok:
                with transaction.atomic():
                    event.status = "dispatched"
                    event.dispatch_attempts += 1
                    event.next_retry_at = None
                    event.last_error = ""
                    event.save(update_fields=["status", "dispatch_attempts", "next_retry_at", "last_error"])
                    # A provider status callback may arrive before its HTTP acknowledgement.
                    booking = MarketplaceBooking.objects.select_for_update().get(pk=booking.pk)
                    if booking.status not in {"completed", "cancelled", "failed"}:
                        booking.status = "confirmed"
                        booking.fulfillment_status = "provider_confirmed"
                        booking.save(update_fields=["status", "fulfillment_status", "updated_at"])
                dispatched += 1
                self.stdout.write(self.style.SUCCESS(f"Dispatched {booking.booking_id} to {module_code}"))
            else:
                self._mark_failed(booking, event, detail, dry_run)
                failed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed={processed} dispatched={dispatched} failed={failed} dry_run={dry_run}"
            )
        )

    def _target_url(self, booking):
        module_code = booking.module.code
        connector = AppConnector.objects.filter(
            module=booking.module,
            tenant=booking.tenant,
            is_active=True,
        ).first()
        if connector and connector.base_url:
            return self._connector_url(connector.base_url, module_code)

        env_name = {
            "staylux": "STAYLUX_CONNECTOR_URL",
            "drivesphere": "DRIVESPHERE_CONNECTOR_URL",
            "laundrex": "LAUNDREX_CONNECTOR_URL",
        }.get(module_code)
        configured = os.getenv(env_name, "").strip() if env_name else ""
        if configured:
            return configured.format(tenant_code=booking.tenant.tenant_code)

        connector = AppConnector.objects.filter(module=booking.module, tenant__isnull=True, is_active=True).first()
        if not connector or not connector.base_url:
            return ""

        return self._connector_url(connector.base_url, module_code)

    def _connector_url(self, base_url, module_code):
        base = base_url.rstrip("/")
        endpoint = DEFAULT_ENDPOINTS.get(module_code, "/api/central/bookings/")
        return f"{base}{endpoint}"

    def _post_event(self, target_url, event: ConnectorEvent):
        payload = dict(event.payload or {})
        body = json.dumps(payload).encode("utf-8")
        secret = str(getattr(settings, "CONNECTOR_SHARED_SECRET", "") or "")
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        signature = hmac.new(
            secret.encode("utf-8"),
            f"{timestamp}.{nonce}.".encode("utf-8") + body,
            hashlib.sha256,
        ).hexdigest()
        request = Request(
            target_url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Connector-Secret": secret,
                "X-Connector-Timestamp": timestamp,
                "X-Connector-Nonce": nonce,
                "X-Connector-Signature": signature,
                "X-External-Event-Id": event.external_event_id or "",
                "X-Idempotency-Key": event.idempotency_key or "",
                "X-Tenant-Code": event.tenant.tenant_code if event.tenant_id else "",
            },
        )
        try:
            with urlopen(request, timeout=10) as response:
                response_body = response.read().decode("utf-8")
                if 200 <= response.status < 300:
                    try:
                        response_payload = json.loads(response_body or "{}")
                    except json.JSONDecodeError:
                        return False, "Provider returned invalid JSON."
                    if response_payload.get("ok") is True:
                        return True, response_body
                    return False, response_payload.get("error") or "Provider did not acknowledge the booking."
                return False, f"{response.status}: {response_body}"
        except HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            return False, f"{exc.code}: {detail}"
        except URLError as exc:
            return False, str(exc.reason)
        except Exception as exc:
            return False, str(exc)

    def _mark_failed(self, booking, event, detail, dry_run):
        self.stderr.write(f"{booking.booking_id} dispatch failed: {detail}")
        if dry_run:
            return
        with transaction.atomic():
            event.dispatch_attempts += 1
            event.last_error = str(detail)[:500]
            max_attempts = int(getattr(settings, "CONNECTOR_DISPATCH_MAX_ATTEMPTS", 8))
            if event.dispatch_attempts >= max_attempts:
                event.status = "dead_letter"
                event.next_retry_at = None
                booking.status = "failed"
                booking.fulfillment_status = "failed"
                booking.save(update_fields=["status", "fulfillment_status", "updated_at"])
            else:
                event.status = "dispatch_failed"
                delay_seconds = min(60 * (2 ** (event.dispatch_attempts - 1)), 3600)
                event.next_retry_at = timezone.now() + timedelta(seconds=delay_seconds)
                booking.save(update_fields=["updated_at"])
            event.save(update_fields=["status", "dispatch_attempts", "next_retry_at", "last_error"])
