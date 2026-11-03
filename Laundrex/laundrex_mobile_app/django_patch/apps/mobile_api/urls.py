from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AddressDetailView, AddressListCreateView, BankTransferProofView, DeviceTokenView, LaundryCatalogView, LaundryListView,
    LoginView, OtpSendView, OtpVerifyView, OrderDetailView, OrderListCreateView,
    OrderTrackingView, RegisterView, payment_methods_view,
)

urlpatterns = [
    path("auth/register", RegisterView.as_view()),
    path("auth/login", LoginView.as_view()),
    path("auth/otp/send", OtpSendView.as_view()),
    path("auth/otp/verify", OtpVerifyView.as_view()),
    path("auth/token/refresh", TokenRefreshView.as_view()),

    path("laundries", LaundryListView.as_view()),
    path("laundries/<int:pk>/catalog", LaundryCatalogView.as_view()),

    path("addresses", AddressListCreateView.as_view()),
    path("addresses/<int:pk>", AddressDetailView.as_view()),

    path("orders", OrderListCreateView.as_view()),
    path("orders/<int:pk>", OrderDetailView.as_view()),
    path("orders/<int:pk>/tracking", OrderTrackingView.as_view()),
    path("orders/<int:pk>/bank-transfer-proof", BankTransferProofView.as_view()),

    path("devices", DeviceTokenView.as_view()),

    path("payment-methods", payment_methods_view),
]
