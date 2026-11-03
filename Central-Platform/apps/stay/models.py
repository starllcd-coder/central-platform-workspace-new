from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.tenants.models import Module, Tenant, Unit


class StayBooking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("checked_in", "Checked In"),
        ("checked_out", "Checked Out"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_RULE_CHOICES = [
        ("pay_now", "Pay Now"),
        ("pay_at_property", "Pay At Property"),
        ("add_to_existing_bill", "Add To Existing Bill"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("due_at_property", "Due At Property"),
        ("added_to_bill", "Added To Existing Bill"),
    ]
    BOOKING_TYPE_CHOICES = [
        ("original", "Original"),
        ("extension", "Extension"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="stay_bookings")
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        related_name="stay_bookings",
        null=True,
        blank=True,
    )
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="stay_bookings")
    booking_id = models.CharField(max_length=40, unique=True)
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, default="original")
    parent_booking = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="extensions",
        null=True,
        blank=True,
    )
    billed_to_booking = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="billed_extensions",
        null=True,
        blank=True,
    )
    customer_name = models.CharField(max_length=180, blank=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=50, blank=True)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    payment_rule = models.CharField(max_length=30, choices=PAYMENT_RULE_CHOICES, default="pay_now")
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    currency = models.CharField(max_length=10, default="OMR")
    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.00"))
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_stay_bookings",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "check_in", "check_out"]),
            models.Index(fields=["unit", "check_in", "check_out"]),
            models.Index(fields=["parent_booking"]),
        ]

    @property
    def nights(self):
        return max(0, (self.check_out - self.check_in).days)

    def clean(self):
        if self.check_out <= self.check_in:
            raise ValidationError({"check_out": "check_out must be later than check_in."})
        if self.unit_id and self.tenant_id and self.unit.tenant_id != self.tenant_id:
            raise ValidationError({"unit": "Selected unit does not belong to booking tenant."})
        if self.parent_booking_id and self.parent_booking_id == self.id:
            raise ValidationError({"parent_booking": "Booking cannot be parent of itself."})
        if self.parent_booking_id and self.booking_type != "extension":
            raise ValidationError({"booking_type": "Booking with parent_booking must be extension."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id}:{self.tenant.tenant_code}:{self.unit_id}"


class StayBookingCommission(models.Model):
    STATUS_CHOICES = [
        ("accrued", "Accrued"),
        ("settled", "Settled"),
        ("waived", "Waived"),
    ]

    booking = models.OneToOneField(
        StayBooking,
        on_delete=models.CASCADE,
        related_name="commission_record",
    )
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    commission_amount = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="OMR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="accrued")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.booking.booking_id}:{self.commission_amount}"


class StayBookingPayment(models.Model):
    booking = models.OneToOneField(
        StayBooking,
        on_delete=models.CASCADE,
        related_name="payment_record",
    )
    amount_due = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.00"))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.00"))
    billing_reference = models.CharField(max_length=120, blank=True, default="")
    payment_transaction = models.ForeignKey(
        "billing.PaymentTransaction",
        on_delete=models.SET_NULL,
        related_name="stay_booking_payments",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.booking.booking_id}:{self.amount_paid}/{self.amount_due}"


class StayUnitRate(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="stay_unit_rates")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="stay_unit_rates")
    day = models.DateField()
    nightly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="OMR")

    class Meta:
        unique_together = ("unit", "day")
        ordering = ["-day", "unit_id"]

    def __str__(self):
        return f"{self.unit_id}:{self.day}:{self.nightly_rate}"


class StayUnitAvailability(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("booked", "Booked"),
        ("held", "Held"),
        ("out_of_service", "Out Of Service"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="stay_availability_rows")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="stay_availability_rows")
    day = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    booking = models.ForeignKey(
        StayBooking,
        on_delete=models.SET_NULL,
        related_name="availability_rows",
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("unit", "day")
        ordering = ["-day", "unit_id"]

    def __str__(self):
        return f"{self.unit_id}:{self.day}:{self.status}"
