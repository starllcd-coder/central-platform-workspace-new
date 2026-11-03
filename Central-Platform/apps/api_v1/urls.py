from django.urls import include, path

from apps.ops.views import health_summary_api
from .views import api_v1_health

urlpatterns = [
    path("health/", api_v1_health, name="api-v1-health"),
    path("health/ops-summary/", health_summary_api, name="api-v1-ops-health-summary"),
    path("connectors/", include("apps.connectors.urls")),
    path("marketplace/", include("apps.marketplace.urls")),
]
