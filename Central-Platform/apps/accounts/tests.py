import re
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.tenants.models import Tenant

from .models import MembershipRole, TenantMembership, UserTwoFactor, UserTwoFactorBackupCode
from .twofa import backup_code_hash


class TwoFactorBackupTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="alpha", password="Pass12345!")

    def test_backup_code_can_verify_and_is_consumed(self):
        self.client.login(username="alpha", password="Pass12345!")
        tf = UserTwoFactor.objects.create(user=self.user, secret="JBSWY3DPEHPK3PXP", is_enabled=True)
        code = "1234-5678"
        UserTwoFactorBackupCode.objects.create(two_factor=tf, code_hash=backup_code_hash(code))

        response = self.client.post(reverse("two-factor-verify"), data={"code": code})
        self.assertEqual(response.status_code, 302)
        tf.refresh_from_db()
        self.assertIsNotNone(tf.last_verified_at)
        backup = UserTwoFactorBackupCode.objects.get(two_factor=tf)
        self.assertTrue(backup.is_used)

    @override_settings(TWO_FACTOR_MANDATORY_FOR_SUPERUSER=True)
    def test_mandatory_2fa_redirect_after_login_for_superuser(self):
        User = get_user_model()
        admin = User.objects.create_superuser(username="root", password="RootPass123!", email="root@test.local")
        response = self.client.post(reverse("login"), data={"username": admin.username, "password": "RootPass123!"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("two-factor-setup"), response.url)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class BusinessInvitationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_superuser(
            username="invitation-admin",
            email="admin@example.test",
            password="AdminPass123!",
        )
        self.tenant = Tenant.objects.create(
            tenant_code="INVITE-TENANT",
            name="Invitation Tenant",
            module_type="staylux",
            owner_email="owner@example.test",
        )
        self.client.force_login(self.staff)

    def test_staff_invitation_activates_membership_after_password_setup(self):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("tenant-users-manage", args=[self.tenant.id]),
                {
                    "full_name": "Business Owner",
                    "email": "new-owner@example.test",
                    "access_level": "owner",
                },
            )

        self.assertRedirects(response, reverse("tenant-users-manage", args=[self.tenant.id]))
        user = get_user_model().objects.get(email="new-owner@example.test")
        membership = TenantMembership.objects.get(user=user, tenant=self.tenant)
        self.assertEqual(membership.status, "invited")
        self.assertFalse(user.has_usable_password())
        self.assertTrue(
            MembershipRole.objects.filter(membership=membership, role__code="tenant.owner").exists()
        )
        invitation_url = re.search(r"https?://\S+", mail.outbox[0].body).group(0)

        token_response = self.client.get(urlparse(invitation_url).path)
        self.assertEqual(token_response.status_code, 302)
        activation = self.client.post(
            token_response.url,
            {
                "new_password1": "SecureBusinessPass123!",
                "new_password2": "SecureBusinessPass123!",
            },
        )

        self.assertRedirects(activation, reverse("login"))
        user.refresh_from_db()
        membership.refresh_from_db()
        self.assertTrue(user.check_password("SecureBusinessPass123!"))
        self.assertEqual(membership.status, "active")

    def test_existing_user_is_activated_without_password_reset(self):
        existing = get_user_model().objects.create_user(
            username="existing-business",
            email="existing@example.test",
            password="ExistingPass123!",
        )
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("tenant-users-manage", args=[self.tenant.id]),
                {
                    "full_name": "Existing User",
                    "email": existing.email,
                    "access_level": "member",
                },
            )

        self.assertRedirects(response, reverse("tenant-users-manage", args=[self.tenant.id]))
        membership = TenantMembership.objects.get(user=existing, tenant=self.tenant)
        self.assertEqual(membership.status, "active")
        self.assertTrue(
            MembershipRole.objects.filter(membership=membership, role__code="tenant.member").exists()
        )
        self.assertIn("Access granted", mail.outbox[0].subject)
