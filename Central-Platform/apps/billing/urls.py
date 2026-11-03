from django.urls import path

from .views import (
    billing_list,
    dispute_create,
    dispute_create_api,
    dispute_export_csv,
    dispute_list,
    dispute_update,
    dispute_update_api,
    generate_cash_commission_invoice,
    payout_run,
    refund_process_page,
    transaction_create,
    transaction_create_api,
    transaction_refund_api,
    withdrawal_request_create,
    withdrawal_request_update,
)

urlpatterns = [
    path("", billing_list, name="billing-list"),
    path("transactions/new/", transaction_create, name="billing-transaction-create"),
    path("disputes/", dispute_list, name="billing-disputes"),
    path("disputes/export.csv", dispute_export_csv, name="billing-disputes-export"),
    path("disputes/new/", dispute_create, name="billing-dispute-create"),
    path("disputes/<int:dispute_id>/update/", dispute_update, name="billing-dispute-update"),
    path("payouts/run/", payout_run, name="billing-payout-run"),
    path(
        "cash-invoices/generate/",
        generate_cash_commission_invoice,
        name="billing-cash-invoice-generate",
    ),
    path("withdrawals/new/", withdrawal_request_create, name="billing-withdrawal-create"),
    path(
        "withdrawals/<int:withdrawal_id>/update/",
        withdrawal_request_update,
        name="billing-withdrawal-update",
    ),
    path("transactions/<int:tx_id>/refund/", refund_process_page, name="billing-refund-process"),
    path("api/transactions/", transaction_create_api, name="billing-transaction-create-api"),
    path("api/disputes/", dispute_create_api, name="billing-dispute-create-api"),
    path("api/disputes/<int:dispute_id>/update/", dispute_update_api, name="billing-dispute-update-api"),
    path(
        "api/transactions/<int:tx_id>/refund/",
        transaction_refund_api,
        name="billing-transaction-refund-api",
    ),
]
