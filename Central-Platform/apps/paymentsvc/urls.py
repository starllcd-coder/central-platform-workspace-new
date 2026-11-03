from django.urls import path

from .views import (
    create_card_guarantee_api,
    create_payment_api,
    get_payment_status_api,
    process_extension_payment_api,
    refund_payment_api,
    stripe_webhook,
    tap_webhook,
    thawani_webhook,
    verify_payment_api,
)

urlpatterns = [
    path("api/create-payment/", create_payment_api, name="paymentsvc-create-payment"),
    path("api/verify-payment/", verify_payment_api, name="paymentsvc-verify-payment"),
    path("api/refund-payment/", refund_payment_api, name="paymentsvc-refund-payment"),
    path("api/get-payment-status/", get_payment_status_api, name="paymentsvc-get-payment-status"),
    path("api/create-card-guarantee/", create_card_guarantee_api, name="paymentsvc-create-card-guarantee"),
    path("api/process-extension-payment/", process_extension_payment_api, name="paymentsvc-process-extension-payment"),
    path("webhooks/thawani/", thawani_webhook, name="paymentsvc-webhook-thawani"),
    path("webhooks/tap/", tap_webhook, name="paymentsvc-webhook-tap"),
    path("webhooks/stripe/", stripe_webhook, name="paymentsvc-webhook-stripe"),
]

