from django.db import models

from apps.tenants.models import Module, Tenant


class AppConnector(models.Model):
    AUTH_MODE_CHOICES = [
        ("shared_secret", "Shared Secret"),
        ("none", "None"),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="connectors")
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="app_connectors",
        help_text="Tenant-specific destination. Leave blank only for a single-instance module fallback.",
    )
    base_url = models.URLField(max_length=255, blank=True)
    public_url = models.URLField(max_length=255, blank=True)
    health_endpoint = models.CharField(max_length=120, default="/health")
    auth_mode = models.CharField(max_length=30, choices=AUTH_MODE_CHOICES, default="shared_secret")
    api_key = models.CharField(max_length=180, blank=True)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["module", "tenant"], name="unique_module_tenant_connector"),
            models.UniqueConstraint(
                fields=["module"],
                condition=models.Q(tenant__isnull=True),
                name="unique_default_module_connector",
            ),
        ]

    def __str__(self):
        tenant_code = self.tenant.tenant_code if self.tenant_id else "default"
        return f"{self.module.code}:{tenant_code} connector"


class ConnectorEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ("tenant.sync", "Tenant Sync"),
        ("usage.report", "Usage Report"),
        ("webhook.event", "Webhook Event"),
    ]

    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connector_events",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connector_events",
    )
    payload = models.JSONField(default=dict)
    external_event_id = models.CharField(max_length=120, blank=True, default="", db_index=True)
    idempotency_key = models.CharField(max_length=120, blank=True, default="", db_index=True)
    request_signature = models.CharField(max_length=255, blank=True, default="")
    signature_valid = models.BooleanField(default=False)
    auth_key_version = models.CharField(max_length=20, blank=True, default="")
    source_timestamp = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="accepted")
    dispatch_attempts = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_error = models.CharField(max_length=500, blank=True, default="")
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["event_type", "external_event_id"]),
            models.Index(fields=["event_type", "idempotency_key"]),
        ]

    def __str__(self):
        return f"{self.event_type}:{self.id}"


class ConnectorRequestNonce(models.Model):
    nonce = models.CharField(max_length=120, unique=True)
    event_type = models.CharField(max_length=30, default="")
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connector_nonces",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connector_nonces",
    )
    source_timestamp = models.DateTimeField(null=True, blank=True)
    request_signature = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["module", "created_at"]),
            models.Index(fields=["tenant", "created_at"]),
        ]

    def __str__(self):
        return f"{self.nonce}:{self.event_type}"


class ConnectorHealthLog(models.Model):
    endpoint = models.CharField(max_length=120)
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connector_health_logs",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connector_health_logs",
    )
    status_code = models.IntegerField(default=200)
    is_success = models.BooleanField(default=True)
    auth_key_version = models.CharField(max_length=20, blank=True, default="")
    reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["endpoint", "created_at"]),
            models.Index(fields=["is_success", "created_at"]),
        ]

    def __str__(self):
        return f"{self.endpoint}:{self.status_code}:{self.is_success}"
