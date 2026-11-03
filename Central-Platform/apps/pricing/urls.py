from django.urls import path

from .views import (
    add_on_create,
    add_ons_api,
    commission_rule_create,
    commission_rule_edit,
    commission_rule_status_api,
    commission_rule_toggle,
    commission_rules_api,
    feature_check_api,
    pricing_transition_apply,
    pricing_transition_apply_api,
    pricing_transition_create,
    pricing_transitions_api,
    tenant_add_on_subscribe,
    tenant_add_ons_api,
    pricing_list,
)

urlpatterns = [
    path("", pricing_list, name="pricing-list"),
    path("commission-rules/new/", commission_rule_create, name="commission-rule-create"),
    path(
        "commission-rules/<int:rule_id>/edit/",
        commission_rule_edit,
        name="commission-rule-edit",
    ),
    path(
        "commission-rules/<int:rule_id>/toggle/",
        commission_rule_toggle,
        name="commission-rule-toggle",
    ),
    path("api/commission-rules/", commission_rules_api, name="commission-rules-api"),
    path(
        "api/commission-rules/<int:rule_id>/status/",
        commission_rule_status_api,
        name="commission-rule-status-api",
    ),
    path("api/features/check/", feature_check_api, name="feature-check-api"),
    path("add-ons/new/", add_on_create, name="pricing-add-on-create"),
    path("tenant-add-ons/new/", tenant_add_on_subscribe, name="pricing-tenant-add-on-subscribe"),
    path("transitions/new/", pricing_transition_create, name="pricing-transition-create"),
    path(
        "transitions/<int:transition_id>/apply/",
        pricing_transition_apply,
        name="pricing-transition-apply",
    ),
    path("api/transitions/", pricing_transitions_api, name="pricing-transitions-api"),
    path(
        "api/transitions/<int:transition_id>/apply/",
        pricing_transition_apply_api,
        name="pricing-transition-apply-api",
    ),
    path("api/add-ons/", add_ons_api, name="pricing-add-ons-api"),
    path("api/tenant-add-ons/", tenant_add_ons_api, name="pricing-tenant-add-ons-api"),
]
