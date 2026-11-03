from django.db import models

from apps.tenants.models import Module, Tenant


class GatewayProvider(models.TextChoices):
    THAWANI = "thawani", "Thawani"
    TAP = "tap", "Tap Payments"
    STRIPE = "stripe", "Stripe"


class PaymentStatus(models.TextChoices):
    CREATED = "created", "Created"
    PENDING = "pending", "Pending"
    AUTHORIZED = "authorized", "Authorized"
    CAPTURED = "captured", "Captured"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"
    PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"
    EXPIRED = "expired", "Expired"


class GatewayConfig(models.Model):
    provider = models.CharField(max_length=20, choices=GatewayProvider.choices, unique=True)
    is_enabled = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=100)
    api_base_url = models.CharField(max_length=255, blank=True, default="")
    public_key = models.CharField(max_length=255, blank=True, default="")
    secret_key_encrypted = models.TextField(blank=True, default="")
    webhook_secret_encrypted = models.TextField(blank=True, default="")
    supports_partial_refund = models.BooleanField(default=True)
    supports_card_guarantee = models.BooleanField(default=True)
    settings_json = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "provider"]

    def __str__(self):
        return f"{self.provider} ({'on' if self.is_enabled else 'off'})"

    def set_secret_key(self, value):
        from apps.tenants.database_crypto import encrypt_database_secret

        self.secret_key_encrypted = encrypt_database_secret(value)

    def get_secret_key(self):
        from apps.tenants.database_crypto import decrypt_database_secret

        return decrypt_database_secret(self.secret_key_encrypted)

    def set_webhook_secret(self, value):
        from apps.tenants.database_crypto import encrypt_database_secret

        self.webhook_secret_encrypted = encrypt_database_secret(value)

    def get_webhook_secret(self):
        from apps.tenants.database_crypto import decrypt_database_secret

        return decrypt_database_secret(self.webhook_secret_encrypted)


class RoutingRule(models.Model):
    name = models.CharField(max_length=120)
    is_enabled = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=100)
    gateway = models.CharField(max_length=20, choices=GatewayProvider.choices)
    countries_csv = models.CharField(max_length=255, blank=True, default="")
    currencies_csv = models.CharField(max_length=255, blank=True, default="")
    module_codes_csv = models.CharField(max_length=255, blank=True, default="")
    payment_methods_csv = models.CharField(max_length=255, blank=True, default="")
    notes = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "id"]

    def __str__(self):
        return f"{self.name}:{self.gateway}"


class CentralPayment(models.Model):
    payment_id = models.CharField(max_length=64, unique=True)
    external_reference = models.CharField(max_length=120, blank=True, default="", db_index=True)
    idempotency_key = models.CharField(max_length=120, blank=True, default="", db_index=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="central_payments")
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, related_name="central_payments", null=True, blank=True)
    booking_id = models.CharField(max_length=80, blank=True, default="")
    parent_booking_id = models.CharField(max_length=80, blank=True, default="")
    customer_id = models.CharField(max_length=80, blank=True, default="")
    business_id = models.CharField(max_length=80, blank=True, default="")
    gateway_name = models.CharField(max_length=20, choices=GatewayProvider.choices)
    payment_method = models.CharField(max_length=40, default="card")
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    currency = models.CharField(max_length=10, default="OMR")
    country_code = models.CharField(max_length=2, blank=True, default="")
    transaction_status = models.CharField(max_length=30, choices=PaymentStatus.choices, default=PaymentStatus.CREATED)
    refund_status = models.CharField(max_length=30, default="none")
    commission_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    business_share = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    is_card_guarantee = models.BooleanField(default=False)
    is_extension_payment = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    last_error = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "module", "transaction_status"]),
            models.Index(fields=["booking_id"]),
            models.Index(fields=["external_reference"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="payment_amount_positive"),
            models.UniqueConstraint(
                fields=["tenant", "idempotency_key"],
                condition=~models.Q(idempotency_key=""),
                name="unique_tenant_payment_idempotency",
            ),
        ]

    def __str__(self):
        return f"{self.payment_id}:{self.gateway_name}:{self.amount}"


class CentralRefund(models.Model):
    payment = models.ForeignKey(CentralPayment, on_delete=models.CASCADE, related_name="refunds")
    idempotency_key = models.CharField(max_length=120, blank=True, default="")
    refund_id = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    is_partial = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=30, default="processed")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["payment", "idempotency_key"], condition=~models.Q(idempotency_key=""), name="unique_payment_refund_key"),
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="refund_amount_positive"),
        ]

    def __str__(self):
        return f"{self.refund_id}:{self.amount}"


class PaymentWebhookLog(models.Model):
    provider = models.CharField(max_length=20, choices=GatewayProvider.choices)
    event_id = models.CharField(max_length=120, blank=True, default="", db_index=True)
    signature_valid = models.BooleanField(default=False)
    payload = models.JSONField(default=dict, blank=True)
    processing_status = models.CharField(max_length=30, default="received")
    detail = models.CharField(max_length=255, blank=True, default="")
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "event_id"],
                condition=~models.Q(event_id=""),
                name="unique_provider_webhook_event",
            ),
        ]

    def __str__(self):
        return f"{self.provider}:{self.event_id}:{self.processing_status}"


class PaymentRequestNonce(models.Model):
    nonce = models.CharField(max_length=120, unique=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    source_timestamp = models.DateTimeField()
    request_signature = models.CharField(max_length=128)
    auth_key_version = models.CharField(max_length=20, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{self.nonce}:{self.method}:{self.path}"
