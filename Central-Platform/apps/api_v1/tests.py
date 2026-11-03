import json

from django.test import TestCase
from django.urls import reverse


class ApiV1HealthTests(TestCase):
    def test_api_v1_health_envelope(self):
        res = self.client.get(reverse("api-v1-health"))
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body.get("ok"), True)
        self.assertEqual(body.get("api_version"), "v1")
