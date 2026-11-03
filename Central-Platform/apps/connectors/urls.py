from django.urls import path

from .views import connector_api_docs, connector_health, tenant_sync, usage_report, webhook_events

urlpatterns = [
    path("docs/", connector_api_docs, name="connector-api-docs"),
    path("health/", connector_health, name="connector-health"),
    path("tenant/sync/", tenant_sync, name="connector-tenant-sync"),
    path("usage/report/", usage_report, name="connector-usage-report"),
    path("webhooks/events/", webhook_events, name="connector-webhooks-events"),
]
