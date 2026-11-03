from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.tenants.models import Module, Tenant


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=120)
    entity_type = models.CharField(max_length=80, blank=True)
    entity_id = models.CharField(max_length=80, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action}:{self.entity_type}:{self.entity_id}"


class NotificationTemplate(models.Model):
    CHANNEL_CHOICES = [
        ("in_app", "In-App"),
        ("email", "Email"),
        ("sms", "SMS"),
        ("webhook", "Webhook"),
    ]

    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="in_app")
    subject_template = models.CharField(max_length=180, blank=True)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class NotificationEvent(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_events",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_events",
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_notifications",
    )
    channel = models.CharField(max_length=20, choices=NotificationTemplate.CHANNEL_CHOICES)
    recipient = models.CharField(max_length=180, blank=True)
    subject = models.CharField(max_length=180, blank=True)
    body = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    last_error = models.CharField(max_length=255, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    external_id = models.CharField(max_length=120, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.channel}:{self.status}:{self.recipient or 'n/a'}"


class OccupancySnapshot(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="occupancy_snapshots",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="occupancy_snapshots",
        null=True,
        blank=True,
    )
    snapshot_date = models.DateField()
    total_units = models.PositiveIntegerField(default=0)
    occupied_units = models.PositiveIntegerField(default=0)
    total_capacity = models.PositiveIntegerField(default=0)
    used_capacity = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=40, default="manual")
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tenant", "module", "snapshot_date")
        ordering = ["-snapshot_date", "-id"]

    def clean(self):
        if self.occupied_units > self.total_units:
            raise ValidationError({"occupied_units": "occupied_units cannot exceed total_units."})
        if self.used_capacity > self.total_capacity:
            raise ValidationError({"used_capacity": "used_capacity cannot exceed total_capacity."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        module_code = self.module.code if self.module else "all"
        return f"{self.tenant.tenant_code}:{module_code}:{self.snapshot_date.isoformat()}"
