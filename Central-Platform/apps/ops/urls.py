from django.urls import path

from .views import (
    analytics_dashboard,
    analytics_export_csv,
    health_summary_api,
    analytics_metrics_api,
    audit_logs_list,
    marketplace_ranking_api,
    marketplace_ranking_dashboard,
    notification_retry,
    notifications_list,
)

urlpatterns = [
    path("notifications/", notifications_list, name="ops-notifications-list"),
    path("notifications/<int:event_id>/retry/", notification_retry, name="ops-notification-retry"),
    path("audit-logs/", audit_logs_list, name="ops-audit-logs-list"),
    path("analytics/", analytics_dashboard, name="ops-analytics-dashboard"),
    path("marketplace-ranking/", marketplace_ranking_dashboard, name="ops-marketplace-ranking"),
    path("api/analytics/metrics/", analytics_metrics_api, name="ops-analytics-metrics-api"),
    path("api/health/summary/", health_summary_api, name="ops-health-summary-api"),
    path("api/analytics/export.csv", analytics_export_csv, name="ops-analytics-export-csv"),
    path("api/marketplace-ranking/", marketplace_ranking_api, name="ops-marketplace-ranking-api"),
]
