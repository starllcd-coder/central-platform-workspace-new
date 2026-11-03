from django import forms

from .models import AddOn, CommissionRule, PricingTransition, TenantAddOnSubscription


class CommissionRuleForm(forms.ModelForm):
    class Meta:
        model = CommissionRule
        fields = [
            "tenant",
            "module",
            "booking_type",
            "rate_percent",
            "fixed_fee",
            "effective_from",
            "effective_to",
            "is_active",
            "notes",
        ]
        widgets = {
            "effective_from": forms.DateInput(attrs={"type": "date"}),
            "effective_to": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional notes"}),
        }

    def clean(self):
        cleaned = super().clean()
        effective_from = cleaned.get("effective_from")
        effective_to = cleaned.get("effective_to")
        if effective_from and effective_to and effective_to < effective_from:
            raise forms.ValidationError("Effective to date cannot be before effective from date.")
        return cleaned


class PricingTransitionForm(forms.ModelForm):
    class Meta:
        model = PricingTransition
        fields = [
            "tenant",
            "target_plan_version",
            "effective_on",
            "notes",
        ]
        widgets = {
            "effective_on": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional migration notes"}),
        }


class AddOnForm(forms.ModelForm):
    class Meta:
        model = AddOn
        fields = ["code", "name", "description", "billing_cycle", "price", "is_active"]
        widgets = {
            "description": forms.TextInput(attrs={"placeholder": "Optional add-on description"}),
        }


class TenantAddOnSubscriptionForm(forms.ModelForm):
    class Meta:
        model = TenantAddOnSubscription
        fields = ["tenant", "add_on", "status", "start_date", "end_date", "notes"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional subscription notes"}),
        }
