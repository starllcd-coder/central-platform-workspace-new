from django.urls import path
from .capabilities import capabilities
from .sso import ticket_api
from .checkout import start_checkout, check_checkout
from .dashboards import partner_dashboard, admin_dashboard
from .quotes import quote_api
from .password_recovery import request_reset, confirm_reset

from .views import (
    api_health,
    booking_confirmation_api,
    business_onboarding_api,
    customer_bookings_api,
    customer_profile_api,
    customer_summary_api,
    listings_api,
    login_api,
    provider_login_api,
    search_api,
    register_api,
    submit_booking_api,
    submit_booking_finalize_api,
    tenants_api,
    payment_session_api,
)

urlpatterns = [
    path("capabilities/", capabilities, name="marketplace-capabilities"),
    path("provider/sso-ticket/", ticket_api, name="provider-sso-ticket"),
    path("checkout/start/", start_checkout, name="marketplace-checkout-start"),
    path("checkout/status/", check_checkout, name="marketplace-checkout-status"),
    path("provider/dashboard/", partner_dashboard, name="provider-dashboard"),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),
    path("quotes/", quote_api, name="marketplace-quotes"),
    path("bookings/confirmation/", booking_confirmation_api, name="marketplace-booking-confirmation"),
    path("auth/password-reset/", request_reset, name="marketplace-password-reset"),
    path("auth/password-reset/confirm/", confirm_reset, name="marketplace-password-reset-confirm"),
    path("health/", api_health, name="marketplace-api-health"),
    path("platform/tenants/", tenants_api, name="marketplace-api-platform-tenants"),
    path("tenants/", tenants_api, name="marketplace-api-tenants"),
    path("listings/", listings_api, name="marketplace-api-listings"),
    path("search/", search_api, name="marketplace-api-search"),
    path("bookings/", submit_booking_api, name="marketplace-api-bookings"),
    path("bookings/finalize/", submit_booking_finalize_api, name="marketplace-api-bookings-finalize"),
    path("payments/session/", payment_session_api, name="marketplace-api-payments-session"),
    path("auth/login/", login_api, name="marketplace-api-login"),
    path("auth/register/", register_api, name="marketplace-api-register"),
    path("customer/profile/", customer_profile_api, name="marketplace-api-customer-profile"),
    path("customer/bookings/", customer_bookings_api, name="marketplace-api-customer-bookings"),
    path("customer/summary/", customer_summary_api, name="marketplace-api-customer-summary"),
    path("leads/", business_onboarding_api, name="marketplace-api-leads"),
    path("business/onboarding/", business_onboarding_api, name="marketplace-api-business-onboarding"),
    path("provider/login/", provider_login_api, name="marketplace-api-provider-login"),
]
