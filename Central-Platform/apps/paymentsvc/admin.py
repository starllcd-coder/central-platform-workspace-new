from django.contrib import admin
from django import forms

from .models import (
    CentralPayment,
    CentralRefund,
    GatewayConfig,
    PaymentWebhookLog,
    RoutingRule,
)


class GatewayConfigAdminForm(forms.ModelForm):
    secret_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave blank to retain the encrypted value.",
    )
    webhook_secret = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave blank to retain the encrypted value.",
    )

    class Meta:
        model = GatewayConfig
        exclude = ("secret_key_encrypted", "webhook_secret_encrypted")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("secret_key"):
            instance.set_secret_key(self.cleaned_data["secret_key"])
        if self.cleaned_data.get("webhook_secret"):
            instance.set_webhook_secret(self.cleaned_data["webhook_secret"])
        if commit:
            instance.save()
            self.save_m2m()
        return instance


@admin.register(GatewayConfig)
class GatewayConfigAdmin(admin.ModelAdmin):
    form = GatewayConfigAdminForm
    list_display = ("provider", "is_enabled", "priority", "supports_partial_refund", "supports_card_guarantee")
    list_filter = ("is_enabled", "provider")


@admin.register(RoutingRule)
class RoutingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "gateway", "priority", "is_enabled")
    list_filter = ("gateway", "is_enabled")
    search_fields = ("name", "countries_csv", "currencies_csv", "module_codes_csv")


@admin.register(CentralPayment)
class CentralPaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "tenant", "module", "gateway_name", "amount", "currency", "transaction_status", "refund_status", "created_at")
    list_filter = ("gateway_name", "transaction_status", "refund_status", "module")
    search_fields = ("payment_id", "booking_id", "external_reference", "idempotency_key")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CentralRefund)
class CentralRefundAdmin(admin.ModelAdmin):
    list_display = ("refund_id", "payment", "amount", "is_partial", "status", "created_at")
    list_filter = ("is_partial", "status")
    search_fields = ("refund_id", "payment__payment_id")


@admin.register(PaymentWebhookLog)
class PaymentWebhookLogAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_id", "signature_valid", "processing_status", "received_at")
    list_filter = ("provider", "signature_valid", "processing_status")
    search_fields = ("event_id",)
