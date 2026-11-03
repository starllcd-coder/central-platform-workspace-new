import hashlib
import hmac
import json
import time

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from apps.tenants.models import Module, Tenant

from .models import ConnectorEvent


class ConnectorSecurityTests(TestCase):
    def setUp(self):
        cache.clear()
        self.tenant = Tenant.objects.create(
            tenant_code="T-LAUNDREX",
            name="Laundrex",
            owner_email="owner@laundrex.test",
        )
        self.module = Module.objects.create(code="LAUNDREX", name="Laundrex")
        self.secret = "test-shared-secret"

    def _signed_headers(self, payload):
        timestamp = str(int(time.time()))
        nonce = f"nonce-{time.time_ns()}"
        body = json.dumps(payload).encode("utf-8")
        signature = hmac.new(
            self.secret.encode("utf-8"),
            f"{timestamp}.{nonce}.".encode("utf-8") + body,
            hashlib.sha256,
        ).hexdigest()
        return {
            "HTTP_X_CONNECTOR_SECRET": self.secret,
            "HTTP_X_CONNECTOR_TIMESTAMP": timestamp,
            "HTTP_X_CONNECTOR_NONCE": nonce,
            "HTTP_X_CONNECTOR_SIGNATURE": signature,
        }

    @override_settings(CONNECTOR_SHARED_SECRET="test-shared-secret", CONNECTOR_REQUIRE_SIGNED_REQUESTS=True)
    def test_tenant_sync_requires_signed_headers_when_enforced(self):
        payload = {
            "tenant_code": self.tenant.tenant_code,
            "module_code": self.module.code,
        }
        response = self.client.post(
            reverse("connector-tenant-sync"),
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CONNECTOR_SECRET=self.secret,
        )
        self.assertEqual(response.status_code, 403)

    @override_settings(CONNECTOR_SHARED_SECRET="test-shared-secret", CONNECTOR_REQUIRE_SIGNED_REQUESTS=True)
    def test_webhook_duplicate_event_is_idempotent(self):
        payload = {
            "tenant_code": self.tenant.tenant_code,
            "module_code": self.module.code,
            "event_name": "system.ping",
            "external_event_id": "evt-001",
        }
        headers = self._signed_headers(payload)

        first = self.client.post(
            reverse("connector-webhooks-events"),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(ConnectorEvent.objects.count(), 1)

        second = self.client.post(
            reverse("connector-webhooks-events"),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json().get("duplicate"), True)
        self.assertEqual(ConnectorEvent.objects.count(), 1)

    @override_settings(CONNECTOR_SHARED_SECRET="test-shared-secret", CONNECTOR_REQUIRE_SIGNED_REQUESTS=True)
    def test_webhook_replay_nonce_is_rejected(self):
        payload = {
            "tenant_code": self.tenant.tenant_code,
            "module_code": self.module.code,
            "event_name": "system.ping",
        }
        headers = self._signed_headers(payload)

        first = self.client.post(
            reverse("connector-webhooks-events"),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(first.status_code, 200)

        replay = self.client.post(
            reverse("connector-webhooks-events"),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(replay.status_code, 409)
        self.assertIn("replay detected", replay.json().get("detail", "").lower())

    @override_settings(API_VERSION="2026-04-19", API_RATE_LIMIT_WINDOW_SECONDS=60, API_RATE_LIMIT_REQUESTS=5)
    def test_api_version_and_rate_headers_are_present(self):
        response = self.client.get(reverse("connector-health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-API-Version"), "2026-04-19")
        self.assertIsNotNone(response.headers.get("X-RateLimit-Limit"))
        self.assertIsNotNone(response.headers.get("X-RateLimit-Remaining"))
        self.assertIsNotNone(response.headers.get("X-RateLimit-Window"))

    @override_settings(
        API_RATE_LIMIT_WINDOW_SECONDS=60,
        API_RATE_LIMIT_REQUESTS=1,
        API_RATE_LIMIT_CONNECTOR_REQUESTS=1,
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "test-rate-limit"}},
    )
    def test_connector_rate_limit_enforced(self):
        first = self.client.get(reverse("connector-health"))
        self.assertEqual(first.status_code, 200)
        second = self.client.get(reverse("connector-health"))
        self.assertEqual(second.status_code, 429)

    @override_settings(CONNECTOR_SHARED_SECRET="test-shared-secret", CONNECTOR_REQUIRE_SIGNED_REQUESTS=True)
    def test_version_mismatch_is_rejected(self):
        payload = {
            "tenant_code": self.tenant.tenant_code,
            "module_code": self.module.code,
            "event_name": "system.ping",
        }
        headers = self._signed_headers(payload)
        headers["HTTP_X_API_VERSION"] = "2020-01-01"
        response = self.client.post(
            reverse("connector-webhooks-events"),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(
        CONNECTOR_SHARED_SECRET="test-shared-secret",
        CONNECTOR_SHARED_SECRET_NEXT="next-secret",
        CONNECTOR_REQUIRE_SIGNED_REQUESTS=True,
    )
    def test_next_secret_is_accepted_during_rotation(self):
        payload = {
            "tenant_code": self.tenant.tenant_code,
            "module_code": self.module.code,
            "event_name": "system.ping",
        }
        timestamp = str(int(time.time()))
        nonce = f"nonce-{time.time_ns()}"
        body = json.dumps(payload).encode("utf-8")
        signature = hmac.new(
            b"next-secret",
            f"{timestamp}.{nonce}.".encode("utf-8") + body,
            hashlib.sha256,
        ).hexdigest()
        response = self.client.post(
            reverse("connector-webhooks-events"),
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CONNECTOR_SECRET="next-secret",
            HTTP_X_CONNECTOR_TIMESTAMP=timestamp,
            HTTP_X_CONNECTOR_NONCE=nonce,
            HTTP_X_CONNECTOR_SIGNATURE=signature,
        )
        self.assertEqual(response.status_code, 200)

    @override_settings(CONNECTOR_SHARED_SECRET="test-shared-secret", CONNECTOR_REQUIRE_SIGNED_REQUESTS=True)
    def test_tenant_sync_rejects_demo_tenant(self):
        self.tenant.account_type = "demo"
        self.tenant.demo_expires_on = time.strftime("%Y-%m-%d")
        self.tenant.save(update_fields=["account_type", "demo_expires_on", "updated_at"])
        payload = {
            "tenant_code": self.tenant.tenant_code,
            "module_code": self.module.code,
        }
        headers = self._signed_headers(payload)
        response = self.client.post(
            reverse("connector-tenant-sync"),
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("demo sandbox", response.json().get("detail", "").lower())
