from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from inventory.models import Unit, UnitType
from settings_app.models import PropertyProfile
from sync_engine.models import SyncConfig, SyncEvent, SyncEventStatus
from sync_engine.services import retry_dead_letters


class SyncEngineTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username="syncuser", password="pass1234")
        self.client.login(username="syncuser", password="pass1234")

    def test_sync_event_is_recorded_on_unit_create(self):
        # TestCase never commits its outer transaction; exercise the real
        # post-commit capture hook explicitly instead of changing sync behavior.
        with self.captureOnCommitCallbacks(execute=True):
            prop = PropertyProfile.objects.create(name_en="Sync Property")
            ut = UnitType.objects.create(
                property_profile=prop,
                business_type=prop.business_type,
                name_en="Standard",
                base_rate=Decimal("10.000"),
            )
            Unit.objects.create(
                property_profile=prop,
                unit_type=ut,
                code="S-101",
                daily_price=Decimal("20.000"),
                monthly_price=Decimal("300.000"),
            )

        self.assertTrue(SyncEvent.objects.filter(model_label="inventory.unit", operation="create").exists())

    def test_serialization_keeps_prices_file_names_and_related_ids_json_safe(self):
        import json
        from sync_engine.services import serialize_instance
        prop = PropertyProfile.objects.create(name_en="File Property", logo="property/logo/test.png")
        encoded = serialize_instance(prop)
        self.assertEqual(encoded["logo"], "property/logo/test.png")
        self.assertEqual(encoded["id"], prop.pk)
        unit_type = UnitType.objects.create(property_profile=prop, name_en="Decimal type", base_rate=Decimal("12.345"))
        self.assertEqual(serialize_instance(unit_type)["base_rate"], "12.345")
        json.dumps(encoded)

    def test_sync_write_failure_does_not_break_booking_transaction(self):
        from unittest.mock import patch
        from django.db import IntegrityError, transaction
        from sync_engine.services import record_sync_event
        prop = PropertyProfile.objects.create(name_en="Safe Property")
        with self.assertLogs("sync_engine.services", level="ERROR"):
            with patch("sync_engine.services.SyncEvent.objects.create", side_effect=IntegrityError("unavailable")):
                with transaction.atomic():
                    record_sync_event(instance=prop, operation="update")
                    self.assertTrue(PropertyProfile.objects.filter(pk=prop.pk).exists())

    def test_sync_status_endpoint_returns_queue_counts(self):
        SyncConfig.objects.get_or_create(id=1)
        response = self.client.get("/api/sync/status/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("config", payload)
        self.assertIn("queue", payload)

    def test_sync_outbox_endpoint_returns_events(self):
        cfg, _ = SyncConfig.objects.get_or_create(id=1)
        cfg.shared_secret = "abc123"
        cfg.save(update_fields=["shared_secret", "updated_at"])
        event = SyncEvent.objects.create(
            source_node="node-a",
            model_label="inventory.unit",
            object_pk="10",
            operation="update",
            payload={"code": "A-10"},
        )

        response = self.client.get(
            "/api/sync/events/outbox/",
            HTTP_X_SYNC_SECRET="abc123",
            data={"exclude_source_node": "node-b"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["events"][0]["event_uuid"], str(event.event_uuid))

    def test_retry_dead_letters_requeues_events(self):
        ev = SyncEvent.objects.create(
            source_node="node-a",
            model_label="inventory.unit",
            object_pk="50",
            operation="create",
            payload={"code": "Z-50"},
            status=SyncEventStatus.FAILED,
            is_dead_letter=True,
            attempts=10,
        )
        changed = retry_dead_letters(limit=10)
        self.assertEqual(changed, 1)
        ev.refresh_from_db()
        self.assertFalse(ev.is_dead_letter)
        self.assertEqual(ev.status, SyncEventStatus.PENDING)
