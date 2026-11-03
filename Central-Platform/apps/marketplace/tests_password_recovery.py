import json
from urllib.parse import urlsplit, parse_qs
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", NEXIVO_PUBLIC_URL="https://nexivo.example")
class PasswordRecoveryTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(username="customer@example.com", email="customer@example.com", password="old-password-987")

    def request(self, email):
        return self.client.post(reverse("marketplace-password-reset"), json.dumps({"email": email}), content_type="application/json")

    def confirm(self, query, password="new-password-very-strong-987"):
        return self.client.post(reverse("marketplace-password-reset-confirm"), json.dumps({"uid": query["uid"][0], "token": query["token"][0], "password": password}), content_type="application/json")

    def reset_query(self):
        self.assertEqual(self.request(self.user.email).status_code, 200)
        link = next(line for line in mail.outbox[-1].body.splitlines() if line.startswith("https://"))
        self.assertTrue(link.startswith("https://nexivo.example/reset-password?"))
        return parse_qs(urlsplit(link).query)

    def test_known_and_unknown_accounts_have_same_response_and_email_is_throttled(self):
        known = self.request(self.user.email)
        unknown = self.request("unknown@example.com")
        self.assertEqual(known.json(), unknown.json())
        self.request(self.user.email)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_changes_and_link_cannot_be_reused(self):
        query = self.reset_query()
        self.assertEqual(self.confirm(query).status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-password-very-strong-987"))
        self.assertEqual(self.confirm(query).status_code, 400)

    def test_invalid_token_and_weak_password_do_not_change_password(self):
        query = self.reset_query()
        self.assertEqual(self.confirm(query, "short").status_code, 400)
        query["token"] = ["invalid"]
        self.assertEqual(self.confirm(query).status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("old-password-987"))

    def test_inactive_accounts_do_not_receive_reset_email(self):
        self.user.is_active = False
        self.user.save()
        self.assertEqual(self.request(self.user.email).status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_revokes_only_affected_customer_tokens(self):
        from .views import _issue_token
        other = get_user_model().objects.create_user(username="other@example.com", email="other@example.com", password="other-password-987")
        old_token = _issue_token(self.user.pk, self.user.email)
        other_token = _issue_token(other.pk, other.email)
        self.assertEqual(self.confirm(self.reset_query()).status_code, 200)
        self.assertEqual(self.client.get(reverse("marketplace-api-customer-profile"), HTTP_AUTHORIZATION=f"Bearer {old_token}").status_code, 401)
        self.assertEqual(self.client.get(reverse("marketplace-api-customer-profile"), HTTP_AUTHORIZATION=f"Bearer {other_token}").status_code, 200)
        new_token = _issue_token(self.user.pk, self.user.email)
        self.assertEqual(self.client.get(reverse("marketplace-api-customer-profile"), HTTP_AUTHORIZATION=f"Bearer {new_token}").status_code, 200)
