from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.connectors.models import ConnectorHealthLog
from apps.ops.models import NotificationEvent
from apps.ops.services import dispatch_notification


class OpsHealthMonitorTests(TestCase):
    @override_settings(DEBUG=False, SMS_PROVIDER="mock")
    def test_mock_sms_is_not_reported_as_sent_outside_debug(self):
        event = NotificationEvent.objects.create(
            channel="sms",
            recipient="+96890000000",
            body="Test",
            status="pending",
        )

        self.assertFalse(dispatch_notification(event))
        event.refresh_from_db()
        self.assertEqual(event.status, "failed")
        self.assertEqual(event.external_id, "")

    @override_settings(
        OPS_ALERT_WINDOW_MINUTES=30,
        OPS_ALERT_MAX_FAILED_NOTIFICATIONS=1,
        OPS_ALERT_MAX_CONNECTOR_FAILURES=1,
    )
    def test_monitor_platform_health_emits_alert_notification(self):
        NotificationEvent.objects.create(
            channel="in_app",
            body="failed row",
            status="failed",
        )
        ConnectorHealthLog.objects.create(
            endpoint="webhook.event",
            status_code=500,
            is_success=False,
            reason="simulated",
        )

        call_command("monitor_platform_health")

        alert = NotificationEvent.objects.filter(subject="Platform Health Alert").first()
        self.assertIsNotNone(alert)

    def test_health_summary_api_returns_status(self):
        User = get_user_model()
        user = User.objects.create_user(username="opsuser", password="Pass12345!")
        self.client.login(username="opsuser", password="Pass12345!")

        # Permission guard uses reports.view; without RBAC setup this returns redirect/deny.
        # Superuser keeps test focused on API behavior.
        user.is_superuser = True
        user.is_staff = True
        user.save(update_fields=["is_superuser", "is_staff"])
        self.client.login(username="opsuser", password="Pass12345!")

        NotificationEvent.objects.create(channel="in_app", body="failed row", status="failed")
        ConnectorHealthLog.objects.create(endpoint="webhook.event", status_code=500, is_success=False, reason="simulated")

        response = self.client.get(reverse("ops-health-summary-api"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("status", payload)
        self.assertIn(payload["status"], {"healthy", "warning", "critical"})
