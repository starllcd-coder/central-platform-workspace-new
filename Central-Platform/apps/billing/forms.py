from django import forms
from django.utils import timezone

from .models import DisputeCase, PaymentTransaction


class PaymentTransactionForm(forms.ModelForm):
    class Meta:
        model = PaymentTransaction
        fields = [
            "tenant",
            "module",
            "booking_ref",
            "payment_channel",
            "booking_type",
            "gross_amount",
            "gateway_fee",
            "tax_amount",
            "currency",
            "occurred_at",
            "metadata",
        ]
        widgets = {
            "occurred_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get("occurred_at"):
            self.initial["occurred_at"] = timezone.localtime().strftime("%Y-%m-%dT%H:%M")


class PayoutRunForm(forms.Form):
    notes = forms.CharField(required=False, max_length=255)


class CommissionInvoiceGenerateForm(forms.Form):
    tenant = forms.ModelChoiceField(queryset=None)
    due_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    notes = forms.CharField(required=False, max_length=255)

    def __init__(self, *args, **kwargs):
        tenant_queryset = kwargs.pop("tenant_queryset")
        super().__init__(*args, **kwargs)
        self.fields["tenant"].queryset = tenant_queryset


class RefundProcessForm(forms.Form):
    refund_type = forms.ChoiceField(
        choices=[("full", "Full Refund"), ("partial", "Partial Refund")]
    )
    refund_percent = forms.DecimalField(min_value=0, max_value=100, initial=100, decimal_places=2)
    reason = forms.CharField(required=False, max_length=255)


class DisputeCreateForm(forms.ModelForm):
    class Meta:
        model = DisputeCase
        fields = [
            "tenant",
            "transaction",
            "reason",
            "description",
        ]


class DisputeResolveForm(forms.ModelForm):
    class Meta:
        model = DisputeCase
        fields = [
            "status",
            "resolution_type",
            "resolution_notes",
        ]


class WithdrawalRequestCreateForm(forms.Form):
    amount = forms.DecimalField(min_value=0.01, decimal_places=2, max_digits=12)
    notes = forms.CharField(required=False, max_length=255)


class WithdrawalRequestActionForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ("approve", "Approve"),
            ("reject", "Reject"),
            ("mark_paid", "Mark Paid"),
        ]
    )
    notes = forms.CharField(required=False, max_length=255)
