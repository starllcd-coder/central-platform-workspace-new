from django.contrib import admin
from .models import (
    AgreementDocument,
    Branch,
    DemoTenantRequest,
    MarketplaceListing,
    Module,
    Tenant,
    TenantBranding,
    TenantAgreementAcceptance,
    TenantDatabaseConfiguration,
    TenantModule,
    Unit,
)


@admin.register(TenantDatabaseConfiguration)
class TenantDatabaseConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "module_code",
        "mode",
        "engine",
        "status",
        "activate_tenant_status",
        "host",
        "database_name",
        "updated_at",
    )
    list_filter = ("mode", "engine", "status", "module_code")
    search_fields = ("tenant__tenant_code", "tenant__name", "database_name", "username")
    readonly_fields = (
        "password_encrypted",
        "status",
        "failure_reason",
        "provisioned_at",
        "created_at",
        "updated_at",
    )


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tenant_code',
        'account_type',
        'demo_expires_on',
        'module_type',
        'pricing_model',
        'commission_enabled',
        'subscription_status',
        'status',
        'created_at',
    )
    search_fields = ('name', 'tenant_code', 'owner_email')
    list_filter = ('account_type', 'status', 'module_type', 'pricing_model', 'commission_enabled', 'subscription_status')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code')


@admin.register(TenantModule)
class TenantModuleAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'module', 'enabled', 'created_at')
    list_filter = ('enabled', 'module')


@admin.register(AgreementDocument)
class AgreementDocumentAdmin(admin.ModelAdmin):
    list_display = ("code", "version", "document_type", "effective_from", "is_active")
    list_filter = ("document_type", "is_active")
    search_fields = ("code", "title", "version")


@admin.register(TenantAgreementAcceptance)
class TenantAgreementAcceptanceAdmin(admin.ModelAdmin):
    list_display = ("tenant", "document", "accepted_by", "accepted_at")
    list_filter = ("document__document_type",)
    search_fields = ("tenant__tenant_code", "document__code", "document__version")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("tenant", "code", "name", "city", "status", "created_at")
    list_filter = ("status", "tenant")
    search_fields = ("tenant__tenant_code", "code", "name", "city")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("tenant", "branch", "code", "name", "unit_type", "capacity", "status")
    list_filter = ("status", "tenant", "branch")
    search_fields = ("tenant__tenant_code", "branch__code", "code", "name")


@admin.register(TenantBranding)
class TenantBrandingAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "brand_name",
        "custom_domain",
        "domain_verification_status",
        "is_active",
        "updated_at",
    )
    list_filter = ("is_active", "domain_verification_status")
    search_fields = ("tenant__tenant_code", "tenant__name", "brand_name", "custom_domain")


@admin.register(DemoTenantRequest)
class DemoTenantRequestAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "source",
        "product_interest",
        "module_type",
        "requested_duration_days",
        "status",
        "requested_by",
        "reviewed_by",
        "approved_tenant",
        "created_at",
    )
    list_filter = ("status", "module_type", "requested_duration_days")
    search_fields = ("business_name", "owner_email", "requested_tenant_code")


@admin.register(MarketplaceListing)
class MarketplaceListingAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "module",
        "base_price",
        "average_rating",
        "rating_count",
        "plan_level_boost",
        "manual_boost",
        "is_active",
        "updated_at",
    )
    list_filter = ("module", "is_active")
    search_fields = ("tenant__tenant_code", "tenant__name", "module__code", "module__name")
