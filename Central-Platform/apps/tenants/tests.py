from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.tenants.database_provisioning import provision_tenant_database
from apps.tenants.domain_verification import verify_branding_custom_domain
from apps.tenants.forms import DemoTenantRequestForm, TenantForm
from apps.tenants.models import DemoTenantRequest, Tenant, TenantBranding, TenantDatabaseConfiguration
from apps.accounts.models import MembershipRole, TenantMembership


def valid_tenant_form_data(**overrides):
    data = {
        "tenant_code": "T-NEW-001",
        "name": "New Tenant",
        "owner_name": "Owner",
        "owner_email": "owner@example.test",
        "owner_phone": "+971500000000",
        "country": "AE",
        "currency": "AED",
        "timezone": "Asia/Dubai",
        "module_type": "staylux",
        "pricing_model": "subscription",
        "commission_enabled": True,
        "subscription_status": "trial",
        "onboarding_date": "2026-06-22",
        "onboarding_fee_paid": False,
        "pricing_version": "v2",
        "status": "trial",
        "database_mode": "managed",
        "database_engine": "postgresql",
        "database_ssl_mode": "require",
    }
    data.update(overrides)
    return data


class TenantDatabaseFormTests(TestCase):
    def test_managed_database_does_not_require_connection_fields(self):
        form = TenantForm(valid_tenant_form_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_customer_owned_database_requires_complete_connection(self):
        form = TenantForm(valid_tenant_form_data(database_mode="customer_owned"))
        self.assertFalse(form.is_valid())
        for field in (
            "database_host",
            "database_port",
            "database_name",
            "database_username",
            "database_password",
        ):
            self.assertIn(field, form.errors)

    def test_customer_owned_database_accepts_complete_connection(self):
        form = TenantForm(
            valid_tenant_form_data(
                database_mode="customer_owned",
                database_engine="mysql",
                database_host="mysql.example.test",
                database_port=3306,
                database_name="staylux_customer",
                database_username="staylux_user",
                database_password="strong-password",
                database_ssl_mode="required",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_demo_form_requires_duration_and_skips_production_pricing_fields(self):
        form = TenantForm(
            valid_tenant_form_data(),
            demo_mode=True,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("demo_duration_days", form.errors)

        form = TenantForm(
            valid_tenant_form_data(
                demo_duration_days=14,
                pricing_model="one_time",
                pricing_version="",
            ),
            demo_mode=True,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["pricing_model"], "subscription")
        self.assertEqual(form.cleaned_data["status"], "trial")

    def test_demo_request_form_rejects_duplicate_requested_tenant_code(self):
        Tenant.objects.create(tenant_code="T-DUP-001", name="Existing")
        form = DemoTenantRequestForm(
            {
                "business_name": "Prospect",
                "requested_tenant_code": "t-dup-001",
                "owner_name": "Owner",
                "owner_email": "owner@example.test",
                "owner_phone": "+971500000009",
                "country": "AE",
                "currency": "AED",
                "timezone": "Asia/Dubai",
                "module_type": "staylux",
                "requested_duration_days": 14,
                "request_notes": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("requested_tenant_code", form.errors)


@override_settings(
    TENANT_DATABASE_ENCRYPTION_KEY="test-only-independent-database-key",
    TENANT_DB_POSTGRES_HOST="postgres.internal",
    TENANT_DB_POSTGRES_PORT=5432,
    TENANT_DB_POSTGRES_SSLMODE="require",
)
class TenantDatabaseProvisioningTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            tenant_code="T-PROVISION-001",
            name="Provision Tenant",
            module_type="drivesphere",
        )

    def test_password_is_encrypted_at_rest(self):
        configuration = TenantDatabaseConfiguration(
            tenant=self.tenant,
            module_code="drivesphere",
            mode="customer_owned",
            engine="postgresql",
        )
        configuration.set_password("plain-secret")
        self.assertNotIn("plain-secret", configuration.password_encrypted)
        self.assertEqual(configuration.get_password(), "plain-secret")

    @patch("apps.tenants.database_provisioning._validate_postgresql")
    @patch("apps.tenants.database_provisioning._deploy_tenant_application", return_value=True)
    @patch("apps.tenants.database_provisioning._provision_managed_postgresql")
    def test_managed_postgresql_database_is_created_and_marked_ready(
        self, mock_provision, mock_deploy, mock_validate
    ):
        self.tenant.status = "paused"
        self.tenant.save(update_fields=["status", "updated_at"])
        configuration = TenantDatabaseConfiguration.objects.create(
            tenant=self.tenant,
            module_code="drivesphere",
            mode="managed",
            engine="postgresql",
            activate_tenant_status="active",
        )

        provision_tenant_database(configuration.id)

        configuration.refresh_from_db()
        self.assertEqual(configuration.status, "ready")
        self.assertEqual(configuration.host, "postgres.internal")
        self.assertTrue(configuration.database_name.startswith("tenant_t_provision_001"))
        self.assertTrue(configuration.username)
        self.assertTrue(configuration.get_password())
        self.assertIsNotNone(configuration.provisioned_at)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.status, "active")
        mock_provision.assert_called_once()
        mock_deploy.assert_called_once()
        mock_validate.assert_called_once()

    @patch("apps.tenants.database_provisioning._validate_postgresql")
    @patch("apps.tenants.database_provisioning._provision_managed_postgresql")
    def test_tenant_stays_paused_when_deployment_provisioner_is_missing(
        self, mock_provision, mock_validate
    ):
        self.tenant.status = "paused"
        self.tenant.save(update_fields=["status", "updated_at"])
        configuration = TenantDatabaseConfiguration.objects.create(
            tenant=self.tenant,
            module_code="drivesphere",
            mode="managed",
            engine="postgresql",
            activate_tenant_status="active",
        )

        provision_tenant_database(configuration.id)

        configuration.refresh_from_db()
        self.tenant.refresh_from_db()
        self.assertEqual(configuration.status, "deployment_pending")
        self.assertEqual(self.tenant.status, "paused")

    @patch(
        "apps.tenants.database_provisioning._validate_postgresql",
        side_effect=RuntimeError("connection refused"),
    )
    def test_customer_owned_validation_failure_is_recorded(self, mock_validate):
        configuration = TenantDatabaseConfiguration(
            tenant=self.tenant,
            module_code="staylux",
            mode="customer_owned",
            engine="postgresql",
            host="db.customer.test",
            port=5432,
            database_name="customer_db",
            username="customer_user",
        )
        configuration.set_password("customer-password")
        configuration.save()

        with self.assertRaisesMessage(RuntimeError, "connection refused"):
            provision_tenant_database(configuration.id)

        configuration.refresh_from_db()
        self.assertEqual(configuration.status, "failed")
        self.assertEqual(configuration.failure_reason, "connection refused")
        mock_validate.assert_called_once()


@override_settings(TENANT_DATABASE_ENCRYPTION_KEY="test-view-database-key")
class TenantDatabaseCreationViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="platform-admin",
            email="admin@example.test",
            password="test-password",
        )
        self.client.force_login(self.user)

    @patch("apps.tenants.tasks.provision_tenant_database_task.delay")
    def test_customer_owned_database_is_saved_and_queued(self, mock_delay):
        form_data = valid_tenant_form_data(
            tenant_code="T-VIEW-001",
            database_mode="customer_owned",
            database_host="customer-db.example.test",
            database_port=5432,
            database_name="customer_staylux",
            database_username="customer_user",
            database_password="customer-secret",
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("tenant-create"), form_data)

        self.assertRedirects(response, reverse("tenant-list"))
        tenant = Tenant.objects.get(tenant_code="T-VIEW-001")
        configuration = tenant.database_configurations.get(module_code="staylux")
        self.assertEqual(tenant.status, "paused")
        self.assertEqual(configuration.activate_tenant_status, "trial")
        self.assertEqual(configuration.mode, "customer_owned")
        self.assertEqual(configuration.status, "pending")
        self.assertEqual(configuration.get_password(), "customer-secret")
        self.assertNotIn("customer-secret", configuration.password_encrypted)
        mock_delay.assert_called_once_with(configuration.id)

    @patch("apps.tenants.tasks.provision_tenant_database_task.delay")
    def test_demo_tenant_flow_sets_demo_fields_and_managed_database(self, mock_delay):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("tenant-demo-create"),
                {
                    "tenant_code": "T-DEMO-001",
                    "name": "Demo Tenant",
                    "owner_name": "Demo Owner",
                    "owner_email": "demo@example.test",
                    "owner_phone": "+971500000001",
                    "country": "AE",
                    "currency": "AED",
                    "timezone": "Asia/Dubai",
                    "module_type": "staylux",
                    "demo_duration_days": "14",
                    "demo_notes": "Sample data only",
                },
            )

        self.assertRedirects(response, reverse("tenant-list"))
        tenant = Tenant.objects.get(tenant_code="T-DEMO-001")
        configuration = tenant.database_configurations.get(module_code="staylux")
        self.assertEqual(tenant.account_type, "demo")
        self.assertEqual(tenant.subscription_status, "trial")
        self.assertEqual(tenant.status, "paused")
        self.assertIsNotNone(tenant.demo_expires_on)
        self.assertEqual(configuration.mode, "managed")
        self.assertEqual(configuration.engine, "postgresql")
        mock_delay.assert_called_once_with(configuration.id)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class DemoTenantRequestWorkflowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.business_user = User.objects.create_user(
            username="business-user",
            email="business@example.test",
            password="test-password",
        )
        self.staff_user = User.objects.create_superuser(
            username="central-admin",
            email="central@example.test",
            password="test-password",
        )

    def test_business_user_can_submit_demo_request(self):
        self.client.force_login(self.business_user)
        response = self.client.post(
            reverse("demo-request-create"),
            {
                "business_name": "Requested Demo Business",
                "requested_tenant_code": "REQ-DEMO-001",
                "owner_name": "Owner",
                "owner_email": "owner@requested-demo.test",
                "owner_phone": "+971500000777",
                "country": "AE",
                "currency": "AED",
                "timezone": "Asia/Dubai",
                "module_type": "drivesphere",
                "requested_duration_days": "7",
                "request_notes": "Please enable sample data",
            },
        )

        self.assertRedirects(response, reverse("my-demo-requests"))
        row = DemoTenantRequest.objects.get(requested_tenant_code="REQ-DEMO-001")
        self.assertEqual(row.status, "requested")
        self.assertEqual(row.requested_by, self.business_user)

    def test_my_demo_requests_only_shows_current_users_requests(self):
        other_user = get_user_model().objects.create_user(
            username="other-business",
            email="other@example.test",
            password="test-password",
        )
        DemoTenantRequest.objects.create(
            requested_by=self.business_user,
            business_name="My Business",
            owner_email="business@example.test",
            module_type="staylux",
        )
        DemoTenantRequest.objects.create(
            requested_by=other_user,
            business_name="Other Business",
            owner_email="other@example.test",
            module_type="laundrex",
        )
        self.client.force_login(self.business_user)

        response = self.client.get(reverse("my-demo-requests"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Business")
        self.assertNotContains(response, "Other Business")

    @patch("apps.tenants.tasks.provision_tenant_database_task.delay")
    def test_staff_approval_creates_demo_tenant(self, mock_delay):
        row = DemoTenantRequest.objects.create(
            requested_by=self.business_user,
            business_name="Approval Prospect",
            requested_tenant_code="REQ-DEMO-002",
            owner_name="Owner",
            owner_email="owner@approval.test",
            owner_phone="+971500000778",
            country="AE",
            currency="AED",
            timezone="Asia/Dubai",
            module_type="staylux",
            requested_duration_days=14,
            request_notes="Needs stay sample data",
        )
        self.client.force_login(self.staff_user)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("demo-request-review", args=[row.id]),
                {
                    "action": "approve",
                    "review_notes": "Approved for sales demo",
                },
            )

        self.assertRedirects(response, reverse("demo-request-list"))
        row.refresh_from_db()
        self.assertEqual(row.status, "approved")
        self.assertEqual(row.reviewed_by, self.staff_user)
        self.assertEqual(row.review_notes, "Approved for sales demo")
        self.assertIsNotNone(row.approved_tenant)
        self.assertEqual(row.approved_tenant.account_type, "demo")
        self.assertEqual(row.approved_tenant.tenant_code, "REQ-DEMO-002")
        mock_delay.assert_called_once()
        self.assertEqual(len(mail.outbox), 2)
        decision_email = next(message for message in mail.outbox if "approved" in message.subject.lower())
        invitation_email = next(message for message in mail.outbox if "set up" in message.subject.lower())
        self.assertEqual(
            set(decision_email.to),
            {"owner@approval.test", "business@example.test"},
        )
        self.assertEqual(invitation_email.to, ["owner@approval.test"])
        invited_user = get_user_model().objects.get(email="owner@approval.test")
        membership = TenantMembership.objects.get(user=invited_user, tenant=row.approved_tenant)
        self.assertEqual(membership.status, "invited")
        self.assertTrue(
            MembershipRole.objects.filter(membership=membership, role__code="tenant.owner").exists()
        )

    def test_staff_rejection_sends_email_with_review_notes(self):
        row = DemoTenantRequest.objects.create(
            requested_by=self.business_user,
            business_name="Rejected Prospect",
            owner_email="owner@rejected.test",
            module_type="laundrex",
        )
        self.client.force_login(self.staff_user)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("demo-request-review", args=[row.id]),
                {"action": "reject", "review_notes": "Business details are incomplete."},
            )

        self.assertRedirects(response, reverse("demo-request-list"))
        row.refresh_from_db()
        self.assertEqual(row.status, "rejected")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Business details are incomplete.", mail.outbox[0].body)

    def test_staff_can_convert_approved_demo_to_paid_production(self):
        tenant = Tenant.objects.create(
            tenant_code="DEMO-CONVERT-001",
            name="Conversion Prospect",
            account_type="demo",
            status="trial",
            subscription_status="trial",
            commission_enabled=False,
            demo_expires_on=timezone.localdate() + timedelta(days=7),
        )
        row = DemoTenantRequest.objects.create(
            requested_by=self.business_user,
            approved_tenant=tenant,
            business_name="Conversion Prospect",
            owner_email="owner@conversion.test",
            module_type="staylux",
            status="approved",
        )
        self.client.force_login(self.staff_user)

        response = self.client.post(reverse("demo-request-convert-to-paid", args=[row.id]))

        self.assertRedirects(response, reverse("demo-request-list"))
        tenant.refresh_from_db()
        self.assertEqual(tenant.account_type, "production")
        self.assertEqual(tenant.status, "active")
        self.assertEqual(tenant.subscription_status, "active")
        self.assertTrue(tenant.commission_enabled)
        self.assertIsNone(tenant.demo_expires_on)
        self.assertIsNotNone(tenant.demo_converted_to_paid_at)

        converted_at = tenant.demo_converted_to_paid_at
        response = self.client.post(reverse("demo-request-convert-to-paid", args=[row.id]))
        self.assertRedirects(response, reverse("demo-request-list"))
        tenant.refresh_from_db()
        self.assertEqual(tenant.demo_converted_to_paid_at, converted_at)

class TenantDomainVerificationTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            tenant_code="T-DOMAIN",
            name="Domain Tenant",
            owner_email="owner@domain.test",
        )
        self.branding = TenantBranding.objects.create(
            tenant=self.tenant,
            brand_name="Domain Tenant",
            custom_domain="app.domain.test",
            domain_verification_status="pending",
            domain_verification_token="abc123token",
        )

    @patch("apps.tenants.domain_verification.resolve_txt_records")
    @patch("apps.tenants.domain_verification.resolve_host_addresses")
    def test_verify_domain_marks_verified_when_dns_is_valid(self, mock_host, mock_txt):
        mock_host.return_value = {"ok": True, "addresses": ["1.2.3.4"], "error": ""}
        mock_txt.return_value = {
            "ok": True,
            "records": [f"cp-verify={self.branding.domain_verification_token}"],
            "error": "",
            "method": "test",
        }

        result = verify_branding_custom_domain(self.branding)
        self.branding.refresh_from_db()
        self.assertTrue(result["verified"])
        self.assertEqual(self.branding.domain_verification_status, "verified")

    @patch("apps.tenants.domain_verification.resolve_txt_records")
    @patch("apps.tenants.domain_verification.resolve_host_addresses")
    def test_verify_domain_fails_when_txt_missing(self, mock_host, mock_txt):
        mock_host.return_value = {"ok": True, "addresses": ["1.2.3.4"], "error": ""}
        mock_txt.return_value = {"ok": True, "records": ["other=value"], "error": "", "method": "test"}

        result = verify_branding_custom_domain(self.branding)
        self.branding.refresh_from_db()
        self.assertFalse(result["verified"])
        self.assertEqual(self.branding.domain_verification_status, "failed")
