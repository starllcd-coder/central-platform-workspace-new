from django.urls import path

from .views import (
    admin_panel,
    booking_extensions_api,
    bookings_api,
    business_dashboard,
    customer_dashboard,
    extension_create_api,
    extension_preview_api,
    report_view,
    unit_rate_create,
)

urlpatterns = [
    path("customer/", customer_dashboard, name="stay-customer-dashboard"),
    path("business/", business_dashboard, name="stay-business-dashboard"),
    path("admin/", admin_panel, name="stay-admin-panel"),
    path("reports/", report_view, name="stay-report"),
    path("rates/new/", unit_rate_create, name="stay-rate-create"),
    path("api/bookings/", bookings_api, name="stay-bookings-api"),
    path("api/bookings/<int:booking_id>/extensions/", booking_extensions_api, name="stay-booking-extensions-api"),
    path("api/bookings/<int:booking_id>/extend/preview/", extension_preview_api, name="stay-extension-preview-api"),
    path("api/bookings/<int:booking_id>/extend/", extension_create_api, name="stay-extension-create-api"),
]
