from django.contrib import admin

from .models import (
    AddOn,
    AddOnFeatureEntitlement,
    CommissionRule,
    Feature,
    Plan,
    PlanFeatureEntitlement,
    PlanVersion,
    PricingTransition,
    SubscriptionInvoice,
    TenantAddOnSubscription,
    TenantFeatureOverride,
    TenantSubscription,
)

admin.site.register(Plan)
admin.site.register(PlanVersion)
admin.site.register(TenantSubscription)
admin.site.register(CommissionRule)
admin.site.register(Feature)
admin.site.register(PlanFeatureEntitlement)
admin.site.register(TenantFeatureOverride)
admin.site.register(PricingTransition)
admin.site.register(AddOn)
admin.site.register(AddOnFeatureEntitlement)
admin.site.register(TenantAddOnSubscription)
admin.site.register(SubscriptionInvoice)
