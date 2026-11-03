from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .models import ConnectorRequestNonce


class ConnectorNoncePruneTests(TestCase):
    def test_prune_connector_nonces_respects_dry_run_and_delete(self):
        old_nonce = ConnectorRequestNonce.objects.create(nonce="old-nonce", event_type="webhook.event")
        ConnectorRequestNonce.objects.filter(pk=old_nonce.pk).update(
            created_at=timezone.now() - timedelta(days=10)
        )
        ConnectorRequestNonce.objects.create(nonce="new-nonce", event_type="webhook.event")

        call_command("prune_connector_nonces", "--days", "7", "--dry-run")
        self.assertEqual(ConnectorRequestNonce.objects.count(), 2)

        call_command("prune_connector_nonces", "--days", "7")
        nonces = set(ConnectorRequestNonce.objects.values_list("nonce", flat=True))
        self.assertEqual(nonces, {"new-nonce"})
