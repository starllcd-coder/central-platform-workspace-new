from django import forms
from django.core.validators import URLValidator
from django.utils import timezone

from .models import (
    Branch,
    DemoTenantRequest,
    Tenant,
    TenantBranding,
    TenantDatabaseConfiguration,
    Unit,
)
from .policies import tenant_grandfathering_errors


class TenantForm(forms.ModelForm):
    DEMO_DURATION_CHOICES = [
        (7, "7 days"),
        (14, "14 days"),
    ]

    database_mode = forms.ChoiceField(
        choices=TenantDatabaseConfiguration.MODE_CHOICES,
        initial="managed",
        label="Database ownership",
    )
    database_engine = forms.ChoiceField(
        choices=TenantDatabaseConfiguration.ENGINE_CHOICES,
        initial="postgresql",
        label="Database engine",
    )
    database_host = forms.CharField(
        required=False,
        label="Database host (customer-owned only)",
    )
    database_port = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=65535,
        label="Database port (customer-owned only)",
    )
    database_name = forms.CharField(
        required=False,
        max_length=128,
        label="Database name (customer-owned only)",
    )
    database_username = forms.CharField(
        required=False,
        max_length=128,
        label="Database username (customer-owned only)",
    )
    database_password = forms.CharField(
        required=False,
        strip=False,
        widget=forms.PasswordInput(render_value=False),
        label="Database password (customer-owned only)",
    )
    database_ssl_mode = forms.CharField(
        required=False,
        initial="require",
        max_length=30,
        label="Database SSL mode (customer-owned only)",
    )
    demo_duration_days = forms.TypedChoiceField(
        required=False,
        choices=DEMO_DURATION_CHOICES,
        coerce=int,
        empty_value=None,
        label="Demo access duration",
    )

    class Meta:
        model = Tenant
        fields = [
            'tenant_code',
            'name',
            'owner_name',
            'owner_email',
            'owner_phone',
            'country',
            'currency',
            'timezone',
            'account_type',
            'module_type',
            'pricing_model',
            'commission_enabled',
            'subscription_status',
            'onboarding_date',
            'onboarding_fee_paid',
            'pricing_version',
            'status',
            'demo_expires_on',
            'demo_notes',
        ]

    def __init__(self, *args, **kwargs):
        self.demo_mode = bool(kwargs.pop("demo_mode", False))
        super().__init__(*args, **kwargs)
        self.fields["module_type"].required = True
        self.fields["account_type"].required = False
        self.fields["account_type"].initial = "demo" if self.demo_mode else "production"
        self.fields["account_type"].widget = forms.HiddenInput()
        self.fields["demo_expires_on"].required = False
        self.fields["demo_expires_on"].widget = forms.HiddenInput()

        if self.demo_mode:
            for field_name in [
                "pricing_model",
                "commission_enabled",
                "subscription_status",
                "onboarding_date",
                "onboarding_fee_paid",
                "pricing_version",
                "status",
            ]:
                self.fields[field_name].required = False
                self.fields[field_name].widget = forms.HiddenInput()
            self.fields["pricing_model"].initial = "subscription"
            self.fields["commission_enabled"].initial = False
            self.fields["subscription_status"].initial = "trial"
            self.fields["onboarding_date"].initial = timezone.localdate()
            self.fields["onboarding_fee_paid"].initial = False
            self.fields["pricing_version"].initial = "v2"
            self.fields["status"].initial = "trial"
            for field_name in [
                "database_mode",
                "database_engine",
                "database_host",
                "database_port",
                "database_name",
                "database_username",
                "database_password",
                "database_ssl_mode",
            ]:
                self.fields.pop(field_name, None)
            self.fields["demo_duration_days"].required = True
            self.fields["demo_notes"].label = "Demo notes"
            self.fields["demo_notes"].help_text = (
                "Use this to note sample-data scope, sandbox restrictions, or planned conversion details."
            )
        else:
            self.fields["demo_duration_days"].widget = forms.HiddenInput()

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("onboarding_date"):
            cleaned["onboarding_date"] = timezone.localdate()

        if self.demo_mode:
            if not cleaned.get("demo_duration_days"):
                self.add_error("demo_duration_days", "Select a demo duration.")
            cleaned["account_type"] = "demo"
            cleaned["pricing_model"] = "subscription"
            cleaned["commission_enabled"] = False
            cleaned["subscription_status"] = "trial"
            cleaned["pricing_version"] = "v2"
            cleaned["status"] = "trial"
            return cleaned

        tenant = Tenant(
            module_type=cleaned.get("module_type") or "",
            pricing_model=cleaned.get("pricing_model") or "one_time",
            commission_enabled=bool(cleaned.get("commission_enabled")),
            subscription_status=cleaned.get("subscription_status") or "inactive",
            onboarding_date=cleaned.get("onboarding_date"),
            pricing_version=(cleaned.get("pricing_version") or "").strip(),
        )
        for issue in tenant_grandfathering_errors(tenant):
            self.add_error(None, issue)

        if cleaned.get("database_mode") == "customer_owned":
            required_fields = {
                "database_host": "Database host is required for a customer-owned database.",
                "database_port": "Database port is required for a customer-owned database.",
                "database_name": "Database name is required for a customer-owned database.",
                "database_username": "Database username is required for a customer-owned database.",
                "database_password": "Database password is required for a customer-owned database.",
            }
            for field, message in required_fields.items():
                if not cleaned.get(field):
                    self.add_error(field, message)
        return cleaned


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ["code", "name", "city", "address", "status"]


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["branch", "code", "name", "unit_type", "status", "capacity"]

    def __init__(self, *args, **kwargs):
        branch_queryset = kwargs.pop("branch_queryset", Branch.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["branch"].queryset = branch_queryset


class TenantBrandingForm(forms.ModelForm):
    class Meta:
        model = TenantBranding
        fields = [
            "brand_name",
            "logo_url",
            "primary_color",
            "accent_color",
            "custom_domain",
            "support_email",
            "is_active",
        ]

    def clean_primary_color(self):
        value = (self.cleaned_data.get("primary_color") or "").strip()
        if not value.startswith("#") or len(value) != 7:
            raise forms.ValidationError("Use hex format like #0f766e.")
        return value

    def clean_accent_color(self):
        value = (self.cleaned_data.get("accent_color") or "").strip()
        if not value.startswith("#") or len(value) != 7:
            raise forms.ValidationError("Use hex format like #0369a1.")
        return value

    def clean_custom_domain(self):
        value = (self.cleaned_data.get("custom_domain") or "").strip().lower()
        if not value:
            return ""
        if "://" in value:
            raise forms.ValidationError("Enter hostname only (example: app.example.com).")
        if "/" in value or " " in value:
            raise forms.ValidationError("Custom domain must be a valid hostname.")

        validator = URLValidator()
        try:
            validator(f"https://{value}")
        except forms.ValidationError as exc:
            raise forms.ValidationError("Custom domain is invalid.") from exc
        return value


class DemoTenantRequestForm(forms.ModelForm):
    module_type = forms.ChoiceField(choices=Tenant.MODULE_TYPE_CHOICES)
    owner_email = forms.EmailField(label="Business user email")
    class Meta:
        model = DemoTenantRequest
        fields = [
            "business_name",
            "requested_tenant_code",
            "owner_name",
            "owner_email",
            "owner_phone",
            "country",
            "currency",
            "timezone",
            "module_type",
            "requested_duration_days",
            "request_notes",
        ]

    def clean_requested_tenant_code(self):
        value = (self.cleaned_data.get("requested_tenant_code") or "").strip().upper()
        if value and Tenant.objects.filter(tenant_code=value).exists():
            raise forms.ValidationError("This tenant code is already in use.")
        return value


class DemoTenantRequestReviewForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ("approve", "Approve"),
            ("reject", "Reject"),
        ]
    )
    module_type = forms.ChoiceField(
        required=False,
        choices=[("", "Use requested product"), *Tenant.MODULE_TYPE_CHOICES],
    )
    review_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))


class TenantUserInvitationForm(forms.Form):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=180)
    access_level = forms.ChoiceField(
        choices=[("owner", "Business Owner"), ("member", "Business Member")]
    )
