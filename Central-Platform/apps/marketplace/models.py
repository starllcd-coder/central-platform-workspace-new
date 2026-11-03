from django.db import models
from django.conf import settings

from apps.connectors.models import ConnectorEvent
from apps.stay.models import StayBooking
from apps.tenants.models import MarketplaceListing, Module, Tenant


class MarketplaceBooking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("failed", "Failed"),
    ]
    FULFILLMENT_STATUS_CHOICES = [
        ("central_confirmed", "Central Confirmed"),
        ("connector_queued", "Connector Queued"),
        ("provider_confirmed", "Provider Confirmed"),
        ("failed", "Failed"),
    ]

    booking_id = models.CharField(max_length=80, unique=True)
    listing = models.ForeignKey(
        MarketplaceListing,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marketplace_bookings",
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, related_name="marketplace_bookings")
    module = models.ForeignKey(Module, on_delete=models.PROTECT, related_name="marketplace_bookings")
    connector_event = models.ForeignKey(
        ConnectorEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marketplace_bookings",
    )
    stay_booking = models.ForeignKey(
        StayBooking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marketplace_bookings",
    )
    customer_name = models.CharField(max_length=180, blank=True)
    customer_email = models.EmailField(blank=True, db_index=True)
    customer_phone = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    fulfillment_status = models.CharField(
        max_length=30,
        choices=FULFILLMENT_STATUS_CHOICES,
        default="connector_queued",
    )
    provider_updated_at = models.DateTimeField(null=True, blank=True)
    payment_status = models.CharField(max_length=40, default="unpaid")
    currency = models.CharField(max_length=10, default="OMR")
    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    payload = models.JSONField(default=dict)
    idempotency_key = models.CharField(max_length=120, blank=True, default="", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["module", "status", "created_at"]),
            models.Index(fields=["tenant", "created_at"]),
            models.Index(fields=["customer_email", "created_at"]),
            models.Index(fields=["idempotency_key"]),
        ]

    def __str__(self):
        return f"{self.booking_id}:{self.module.code}"


class CustomerTokenVersion(models.Model):
    # Existing tokens implicitly have version zero, preserving sessions until reset.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=0)
