from django.urls import path
from central_sync.health import health
from central_sync.payments import payment_update
from central_sync.sso import consume_ticket,begin_login
from .views import receive_booking
from .quote_views import quote_view
urlpatterns = [
    path("health/", health, name="central-health"),
    path("payments/", payment_update, name="central-payments"),
    path("sso/begin/", begin_login, name="central-sso-begin"),path("sso/", consume_ticket, name="central-sso"), path("quote/", quote_view, name="central-quote"), path("bookings/", receive_booking, name="central-booking-receiver")]
