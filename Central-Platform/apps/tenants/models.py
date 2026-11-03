import secrets
import string

from django.conf import settings
from django.db import models
from django.utils import timezone


class Tenant(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("production", "Production"),
        ("demo", "Demo"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("trial", "Trial"),
        ("paused", "Paused"),
    ]
    MODULE_TYPE_CHOICES = [
        ("staylux", "StayLux"),
        ("drivesphere", "DriveSphere"),
        ("laundrex", "Laundrex"),
    ]
    PRICING_MODEL_CHOICES = [
        ("one_time", "One-time"),
        ("subscription", "Subscription"),
        ("hybrid", "Hybrid"),
    ]
    SUBSCRIPTION_STATUS_CHOICES = [
        ("inactive", "Inactive"),
        ("trial", "Trial"),
        ("active", "Active"),
        ("cancelled", "Cancelled"),
    ]

    tenant_code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=180)
    owner_name = models.CharField(max_length=180, blank=True)
    owner_email = models.EmailField(blank=True)
    owner_phone = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=80, blank=True)
    currency = models.CharField(max_length=10, default="OMR")
    timezone = models.CharField(max_length=60, default="Asia/Dubai")
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default="production",
    )
    module_type = models.CharField(
        max_length=20, choices=MODULE_TYPE_CHOICES, blank=True, default=""
    )
    pricing_model = models.CharField(
        max_length=20, choices=PRICING_MODEL_CHOICES, default="one_time"
    )
    commission_enabled = models.BooleanField(default=True)
    subscription_status = models.CharField(
        max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default="inactive"
    )
    onboarding_date = models.DateField(null=True, blank=True)
    onboarding_fee_paid = models.BooleanField(default=False)
    pricing_version = models.CharField(max_length=30, blank=True, default="")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="trial")
    demo_expires_on = models.DateField(null=True, blank=True)
    demo_converted_to_paid_at = models.DateTimeField(null=True, blank=True)
    demo_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.tenant_code})"

    @property
    def is_demo(self):
        return self.account_type == "demo"

    @property
    def is_demo_expired(self):
        if not self.is_demo or not self.demo_expires_on:
            return False
        return self.demo_expires_on < timezone.localdate()


class Module(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TenantModule(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="tenant_modules")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="tenant_modules")
    enabled = models.BooleanField(default=True)
    marketplace_enabled = models.BooleanField(default=False)
    marketplace_activated_at = models.DateTimeField(null=True, blank=True)
    commission_grace_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "module")

    def __str__(self):
        return f"{self.tenant.name} - {self.module.code}"


class TenantDatabaseConfiguration(models.Model):
    MODE_CHOICES = [
        ("managed", "Managed database"),
        ("customer_owned", "Customer-owned database"),
    ]
    ENGINE_CHOICES = [
        ("postgresql", "PostgreSQL / Neon"),
        ("mysql", "MySQL"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("provisioning", "Provisioning"),
        ("validating", "Validating"),
        ("deployment_pending", "Waiting for deployment"),
        ("deploying", "Deploying application"),
        ("ready", "Ready"),
        ("failed", "Failed"),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="database_configurations",
    )
    module_code = models.CharField(max_length=40)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES)
    host = models.CharField(max_length=255, blank=True, default="")
    port = models.PositiveIntegerField(null=True, blank=True)
    database_name = models.CharField(max_length=128, blank=True, default="")
    username = models.CharField(max_length=128, blank=True, default="")
    password_encrypted = models.TextField(blank=True, default="")
    ssl_mode = models.CharField(max_length=30, blank=True, default="require")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    activate_tenant_status = models.CharField(
        max_length=12,
        choices=Tenant.STATUS_CHOICES,
        default="trial",
    )
    failure_reason = models.TextField(blank=True, default="")
    provisioned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "module_code"],
                name="unique_tenant_module_database",
            )
        ]
        ordering = ["tenant_id", "module_code"]

    def set_password(self, value):
        from .database_crypto import encrypt_database_secret

        self.password_encrypted = encrypt_database_secret(value)

    def get_password(self):
        from .database_crypto import decrypt_database_secret

        return decrypt_database_secret(self.password_encrypted)

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.module_code}:{self.mode}"


class AgreementDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ("terms", "Terms of Service"),
        ("commission", "Commission Agreement"),
        ("payment_policy", "Payment Policy"),
        ("privacy", "Privacy Policy"),
    ]

    code = models.CharField(max_length=50)
    title = models.CharField(max_length=180)
    document_type = models.CharField(max_length=30, choices=DOC_TYPE_CHOICES)
    version = models.CharField(max_length=20)
    content = models.TextField()
    effective_from = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("code", "version")
        ordering = ["-effective_from", "-created_at"]

    def __str__(self):
        return f"{self.code}:{self.version}"


class TenantAgreementAcceptance(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="agreement_acceptances"
    )
    document = models.ForeignKey(
        AgreementDocument, on_delete=models.CASCADE, related_name="acceptances"
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agreement_acceptances",
    )
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("tenant", "document")
        ordering = ["-accepted_at"]

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.document.code}:{self.document.version}"


class Branch(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="branches")
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=180)
    city = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "code")
        ordering = ["tenant_id", "name"]

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.code}"


class Unit(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("maintenance", "Maintenance"),
        ("inactive", "Inactive"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="units")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="units")
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=180)
    unit_type = models.CharField(max_length=60, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    capacity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("branch", "code")
        ordering = ["tenant_id", "branch_id", "name"]

    def save(self, *args, **kwargs):
        if self.branch_id and not self.tenant_id:
            self.tenant_id = self.branch.tenant_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.branch.code}:{self.code}"


class MarketplaceListing(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="marketplace_listings",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="marketplace_listings",
    )
    public_slug = models.SlugField(max_length=300, unique=True, blank=True)
    snapshot = models.JSONField(default=dict, blank=True)
    provider_updated_at = models.DateTimeField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    plan_level_boost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    manual_boost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    provider_resource_id = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Room/unit, vehicle, or provider service identifier understood by the provider app.",
    )
    provider_resource_name = models.CharField(max_length=180, blank=True, default="")
    provider_resource_unit = models.CharField(max_length=40, blank=True, default="")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tenant", "module", "provider_resource_id")
        ordering = ["module_id", "tenant_id"]

    def save(self, *args, **kwargs):
        if not self.public_slug:
            from django.utils.text import slugify
            import uuid
            legacy = f"{slugify(self.tenant.name)}-{self.module.code}-{self.tenant_id}"
            self.public_slug = legacy if not type(self).objects.filter(tenant_id=self.tenant_id, module_id=self.module_id).exclude(pk=self.pk).exists() else f"{legacy}-{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.module.code}"


class TenantBranding(models.Model):
    DOMAIN_STATUS_CHOICES = [
        ("not_configured", "Not Configured"),
        ("pending", "Pending Verification"),
        ("verified", "Verified"),
        ("failed", "Verification Failed"),
    ]

    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="branding")
    brand_name = models.CharField(max_length=180, blank=True)
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default="#0f766e")
    accent_color = models.CharField(max_length=7, default="#0369a1")
    custom_domain = models.CharField(max_length=180, blank=True)
    domain_verification_status = models.CharField(
        max_length=20,
        choices=DOMAIN_STATUS_CHOICES,
        default="not_configured",
    )
    domain_verification_token = models.CharField(max_length=32, blank=True, default="")
    domain_verified_at = models.DateTimeField(null=True, blank=True)
    domain_last_checked_at = models.DateTimeField(null=True, blank=True)
    domain_failure_reason = models.CharField(max_length=255, blank=True, default="")
    support_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tenant_id"]

    @staticmethod
    def generate_domain_verification_token():
        alphabet = string.ascii_lowercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(24))

    @property
    def domain_txt_record_value(self):
        if not self.domain_verification_token:
            return ""
        return f"cp-verify={self.domain_verification_token}"

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.brand_name or 'branding'}"


class DemoTenantRequest(models.Model):
    SOURCE_CHOICES = [
        ("central", "Central Platform"),
        ("nexivo", "Nexivo Website"),
    ]
    PRODUCT_INTEREST_CHOICES = [
        *Tenant.MODULE_TYPE_CHOICES,
        ("central-platform", "Central Platform"),
        ("multiple", "Multiple DSS Products"),
    ]
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demo_tenant_requests",
    )
    approved_tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_demo_requests",
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="central")
    external_reference = models.CharField(max_length=120, blank=True, default="")
    business_name = models.CharField(max_length=180)
    requested_tenant_code = models.CharField(max_length=40, blank=True, default="")
    owner_name = models.CharField(max_length=180, blank=True)
    owner_email = models.EmailField(blank=True)
    owner_phone = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=80, blank=True)
    currency = models.CharField(max_length=10, default="OMR")
    timezone = models.CharField(max_length=60, default="Asia/Dubai")
    product_interest = models.CharField(
        max_length=30,
        choices=PRODUCT_INTEREST_CHOICES,
        blank=True,
        default="",
    )
    module_type = models.CharField(
        max_length=20,
        choices=Tenant.MODULE_TYPE_CHOICES,
        blank=True,
        default="",
    )
    requested_duration_days = models.PositiveSmallIntegerField(default=14)
    request_notes = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    review_notes = models.TextField(blank=True, default="")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_demo_tenant_requests",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_reference"],
                condition=~models.Q(external_reference=""),
                name="unique_demo_request_source_reference",
            )
        ]

    def __str__(self):
        return f"DEMO-REQ-{self.id}:{self.business_name}:{self.status}"
