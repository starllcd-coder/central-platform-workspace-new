from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import RememberMeLoginView
from apps.core.views import dashboard, healthz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', RememberMeLoginView.as_view(), name='login'),
    path('accounts/login/', RememberMeLoginView.as_view(), name='accounts-login'),
    path('', include('django.contrib.auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('healthz/', healthz, name='healthz'),
    path('', dashboard, name='dashboard'),
    path('tenants/', include('apps.tenants.urls')),
    path('pricing/', include('apps.pricing.urls')),
    path('billing/', include('apps.billing.urls')),
    path('stay/', include('apps.stay.urls')),
    path('ops/', include('apps.ops.urls')),
    path('api/connectors/', include('apps.connectors.urls')),
    path('api/', include('apps.marketplace.urls')),
    path('api/v1/', include('apps.api_v1.urls')),
    path('payments/', include('apps.paymentsvc.urls')),
]
