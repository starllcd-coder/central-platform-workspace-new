from django import forms

from .models import StayBooking, StayUnitRate


class StayBookingCreateForm(forms.ModelForm):
    class Meta:
        model = StayBooking
        fields = [
            "tenant",
            "unit",
            "customer_name",
            "customer_email",
            "customer_phone",
            "check_in",
            "check_out",
            "guests",
            "payment_rule",
            "notes",
        ]
        widgets = {
            "check_in": forms.DateInput(attrs={"type": "date"}),
            "check_out": forms.DateInput(attrs={"type": "date"}),
        }


class StayExtensionRequestForm(forms.Form):
    parent_booking_id = forms.IntegerField(min_value=1)
    new_check_out = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    selected_unit_id = forms.IntegerField(min_value=1, required=False)
    payment_rule = forms.ChoiceField(choices=StayBooking.PAYMENT_RULE_CHOICES)
    notes = forms.CharField(required=False, max_length=255)


class StayUnitRateForm(forms.ModelForm):
    class Meta:
        model = StayUnitRate
        fields = ["tenant", "unit", "day", "nightly_rate", "currency"]
        widgets = {"day": forms.DateInput(attrs={"type": "date"})}
