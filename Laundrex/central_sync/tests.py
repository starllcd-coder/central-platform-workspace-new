from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch
from django.db import transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from .models import OutboundEvent
from .signals import queue_status
from .worker import flush

class OutboxTests(TestCase):
    @override_settings(CENTRAL_SYNC_ENABLED=False)
    def test_disabled_integration_does_not_touch_database_or_network(self):
        with patch("central_sync.signals.external_id", side_effect=AssertionError("must not inspect bookings")):
            queue_status(None, SimpleNamespace())
        self.assertFalse(OutboundEvent.objects.exists())

    @override_settings(CENTRAL_SYNC_ENABLED=True, CENTRAL_TENANT_CODE="T-ONE", CENTRAL_MODULE_CODE="TEST")
    def test_outbox_joins_originating_transaction_and_never_calls_network(self):
        instance = SimpleNamespace(status="CONFIRMED", updated_at=timezone.now())
        with patch("central_sync.signals.external_id", return_value="NXV-ONE"), patch("central_sync.signals.mapped_status", return_value="confirmed"), patch("central_sync.worker.post_connector") as network:
            try:
                with transaction.atomic():
                    queue_status(None, instance)
                    self.assertEqual(OutboundEvent.objects.count(), 1)
                    raise ValueError("rollback source save")
            except ValueError:
                pass
            self.assertFalse(OutboundEvent.objects.exists())
            network.assert_not_called()

    @patch("central_sync.worker.post_connector")
    def test_offline_retry_preserves_event_identity(self, post):
        event = OutboundEvent.objects.create(payload={"external_event_id": "stable-event"})
        post.side_effect = OSError("offline")
        self.assertEqual(flush()["failed"], 1)
        event.refresh_from_db()
        self.assertEqual(event.status, "pending")
        self.assertEqual(event.attempts, 1)
        self.assertGreater(event.next_attempt_at, timezone.now())
        self.assertEqual(flush(), {"delivered": 0, "failed": 0})
        post.side_effect = None
        post.return_value = {"accepted": True}
        OutboundEvent.objects.filter(pk=event.pk).update(next_attempt_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(flush()["delivered"], 1)
        self.assertEqual(post.call_args.args[1]["external_event_id"], "stable-event")
        event.refresh_from_db()
        self.assertEqual(event.status, "delivered")

    @patch("central_sync.worker.post_connector", return_value={"accepted": True})
    def test_crashed_worker_lease_is_recovered(self, post):
        event = OutboundEvent.objects.create(payload={}, status="sending", next_attempt_at=timezone.now() + timedelta(minutes=5))
        self.assertEqual(flush()["delivered"], 0)
        OutboundEvent.objects.filter(pk=event.pk).update(next_attempt_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(flush()["delivered"], 1)

    @patch("central_sync.worker.post_connector", side_effect=OSError("offline"))
    def test_exhausted_event_is_retained_for_inspection(self, post):
        event = OutboundEvent.objects.create(payload={}, attempts=7)
        self.assertEqual(flush()["failed"], 1)
        event.refresh_from_db()
        self.assertEqual(event.status, "dead")
        self.assertIn("offline", event.last_error)

    @override_settings(CENTRAL_SYNC_ENABLED=True, CENTRAL_TENANT_CODE="T-ONE", CENTRAL_MODULE_CODE="laundrex")
    def test_order_save_automatically_queues_central_status(self):
        from apps.orders.models import Order
        order = Order.objects.create(order_no="NXV-TEST-ONE", total="10.00")
        order.status = Order.Status.DELIVERED
        order.save(update_fields=["status", "updated_at"])
        self.assertEqual(OutboundEvent.objects.count(), 2)
        self.assertEqual(OutboundEvent.objects.order_by("id").last().payload["data"]["status"], "completed")
        order.refresh_from_db()
        self.assertEqual(order.total, 10)

    def test_pruning_preserves_pending_dead_events_and_delivery_identity(self):
        from django.core.management import call_command
        old = timezone.now() - timedelta(days=40)
        delivered = OutboundEvent.objects.create(payload={}, status="delivered", delivered_at=old)
        pending = OutboundEvent.objects.create(payload={}, status="pending")
        dead = OutboundEvent.objects.create(payload={}, status="dead")
        call_command("prune_central_sync", dry_run=True)
        self.assertEqual(OutboundEvent.objects.count(), 3)
        call_command("prune_central_sync")
        self.assertFalse(OutboundEvent.objects.filter(pk=delivered.pk).exists())
        call_command("retry_central_event", str(dead.event_id))
        dead.refresh_from_db()
        self.assertEqual(dead.status, "pending")
        self.assertEqual(OutboundEvent.objects.count(), 2)
