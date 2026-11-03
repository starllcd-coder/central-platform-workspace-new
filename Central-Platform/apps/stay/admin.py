from django.contrib import admin

from .models import (
    StayBooking,
    StayBookingCommission,
    StayBookingPayment,
    StayUnitAvailability,
    StayUnitRate,
)


class StayBookingExtensionInline(admin.TabularInline):
    model = StayBooking
    fk_name = "parent_booking"
    extra = 0
    fields = ("booking_id", "unit", "check_in", "check_out", "total_amount", "payment_status", "status")
    readonly_fields = fields
    can_delete = False


@admin.register(StayBooking)
class StayBookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_id",
        "tenant",
        "unit",
        "booking_type",
        "parent_booking",
        "check_in",
        "check_out",
        "total_amount",
        "payment_status",
        "status",
    )
    list_filter = ("booking_type", "status", "payment_rule", "payment_status", "tenant")
    search_fields = ("booking_id", "tenant__tenant_code", "customer_name", "customer_email")
    inlines = [StayBookingExtensionInline]


@admin.register(StayBookingCommission)
class StayBookingCommissionAdmin(admin.ModelAdmin):
    list_display = ("booking", "commission_rate", "commission_amount", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("booking__booking_id", "booking__tenant__tenant_code")


@admin.register(StayBookingPayment)
class StayBookingPaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount_due", "amount_paid", "billing_reference", "payment_transaction")
    search_fields = ("booking__booking_id", "billing_reference")


@admin.register(StayUnitRate)
class StayUnitRateAdmin(admin.ModelAdmin):
    list_display = ("tenant", "unit", "day", "nightly_rate", "currency")
    list_filter = ("tenant", "currency")
    search_fields = ("tenant__tenant_code", "unit__code", "unit__name")


@admin.register(StayUnitAvailability)
class StayUnitAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("tenant", "unit", "day", "status", "booking")
    list_filter = ("tenant", "status")
    search_fields = ("tenant__tenant_code", "unit__code", "unit__name", "booking__booking_id")
