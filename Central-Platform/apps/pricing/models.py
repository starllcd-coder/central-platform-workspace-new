from django.core.exceptions import ValidationError
from django.db import models

from apps.tenants.models import Module, Tenant


class Plan(models.Model):
    BILLING_CHOICES = [
        ("one_time", "One-time"),
        ("subscription", "Subscription"),
        ("hybrid", "Hybrid"),
    ]

    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50, unique=True)
    billing_type = models.CharField(max_length=20, choices=BILLING_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PlanVersion(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="versions")
    version = models.CharField(max_length=20)
    onboarding_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yearly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("plan", "version")

    def clean(self):
        if self.effective_to and self.effective_to < self.effective_from:
            raise ValidationError(
                {"effective_to": "Effective to date cannot be before effective from date."}
            )

        overlaps = PlanVersion.objects.filter(plan=self.plan).exclude(pk=self.pk)
        overlaps = overlaps.filter(
            models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=self.effective_from)
        )
        if self.effective_to:
            overlaps = overlaps.filter(effective_from__lte=self.effective_to)

        if overlaps.exists():
            raise ValidationError(
                "Plan version effective dates overlap with an existing version for this plan."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plan.code} {self.version}"


class TenantSubscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("trial", "Trial"),
        ("cancelled", "Cancelled"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="subscriptions")
    plan_version = models.ForeignKey(PlanVersion, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trial")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    pricing_version = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.tenant.tenant_code} - {self.plan_version}"


class CommissionRule(models.Model):
    BOOKING_TYPE_CHOICES = [
        ("all", "All"),
        ("online", "Online"),
        ("cash", "Cash"),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="commission_rules",
        null=True,
        blank=True,
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="commission_rules",
        null=True,
        blank=True,
    )
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, default="all")
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2)
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_from", "-created_at"]

    def clean(self):
        if self.effective_to and self.effective_to < self.effective_from:
            raise ValidationError(
                {"effective_to": "Effective to date cannot be before effective from date."}
            )

        if not self.is_active:
            return

        overlaps = CommissionRule.objects.filter(is_active=True).exclude(pk=self.pk)
        overlaps = overlaps.filter(
            tenant_id=self.tenant_id,
            module_id=self.module_id,
            booking_type=self.booking_type,
        )
        overlaps = overlaps.filter(
            models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=self.effective_from)
        )
        if self.effective_to:
            overlaps = overlaps.filter(effective_from__lte=self.effective_to)

        if overlaps.exists():
            raise ValidationError(
                "Active commission rule dates overlap with an existing matching rule."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        tenant_code = self.tenant.tenant_code if self.tenant else "global"
        module_code = self.module.code if self.module else "all-modules"
        return f"{tenant_code}:{module_code}:{self.booking_type}:{self.rate_percent}%"


class Feature(models.Model):
    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    default_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class PlanFeatureEntitlement(models.Model):
    plan_version = models.ForeignKey(
        PlanVersion,
        on_delete=models.CASCADE,
        related_name="feature_entitlements",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="plan_entitlements",
    )
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("plan_version", "feature")
        ordering = ["plan_version_id", "feature__code"]

    def __str__(self):
        return f"{self.plan_version_id}:{self.feature.code}:{self.enabled}"


class TenantFeatureOverride(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="feature_overrides",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="tenant_overrides",
    )
    enabled = models.BooleanField(default=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tenant", "feature")
        ordering = ["tenant_id", "feature__code"]

    def clean(self):
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": "ends_on cannot be before starts_on."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.feature.code}:{self.enabled}"


class AddOn(models.Model):
    BILLING_CYCLE_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("one_time", "One-time"),
    ]

    code = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default="monthly")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.code


class AddOnFeatureEntitlement(models.Model):
    add_on = models.ForeignKey(
        AddOn,
        on_delete=models.CASCADE,
        related_name="feature_entitlements",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name="add_on_entitlements",
    )
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("add_on", "feature")
        ordering = ["add_on_id", "feature__code"]

    def __str__(self):
        return f"{self.add_on.code}:{self.feature.code}:{self.enabled}"


class TenantAddOnSubscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("trial", "Trial"),
        ("cancelled", "Cancelled"),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="add_on_subscriptions",
    )
    add_on = models.ForeignKey(
        AddOn,
        on_delete=models.PROTECT,
        related_name="tenant_subscriptions",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "end_date cannot be before start_date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.add_on.code}:{self.status}"


class PricingTransition(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("applied", "Applied"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="pricing_transitions",
    )
    target_plan_version = models.ForeignKey(
        PlanVersion,
        on_delete=models.PROTECT,
        related_name="pricing_transitions",
    )
    source_subscription = models.ForeignKey(
        TenantSubscription,
        on_delete=models.SET_NULL,
        related_name="transition_source_rows",
        null=True,
        blank=True,
    )
    applied_subscription = models.ForeignKey(
        TenantSubscription,
        on_delete=models.SET_NULL,
        related_name="transition_applied_rows",
        null=True,
        blank=True,
    )
    effective_on = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        related_name="created_pricing_transitions",
        null=True,
        blank=True,
    )
    applied_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        related_name="applied_pricing_transitions",
        null=True,
        blank=True,
    )
    applied_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "effective_on", "-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status", "effective_on"]),
            models.Index(fields=["status", "effective_on"]),
        ]

    def clean(self):
        if self.status == "applied" and self.applied_subscription_id is None:
            raise ValidationError({"applied_subscription": "Applied transition requires applied_subscription."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.target_plan_version}:{self.effective_on}:{self.status}"


class SubscriptionInvoice(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="subscription_invoices",
    )
    subscription = models.ForeignKey(
        TenantSubscription,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    plan_version = models.ForeignKey(
        PlanVersion,
        on_delete=models.PROTECT,
        related_name="subscription_invoices",
    )
    invoice_code = models.CharField(max_length=50, unique=True)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="OMR")
    period_start = models.DateField()
    period_end = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    paid_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        unique_together = ("subscription", "period_start", "period_end")
        indexes = [
            models.Index(fields=["status", "due_date"]),
            models.Index(fields=["tenant", "status"]),
        ]

    def __str__(self):
        return f"{self.invoice_code}:{self.tenant.tenant_code}:{self.status}"
