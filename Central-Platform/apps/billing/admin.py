from django.contrib import admin

from .models import (
    CommissionInvoice,
    DisputeCase,
    LedgerEntry,
    PaymentTransaction,
    PayoutBatch,
    RefundRecord,
    Settlement,
    WalletAccount,
    WalletTransaction,
    WithdrawalRequest,
)

admin.site.register(PaymentTransaction)
admin.site.register(LedgerEntry)
admin.site.register(PayoutBatch)
admin.site.register(Settlement)
admin.site.register(CommissionInvoice)
admin.site.register(RefundRecord)
admin.site.register(DisputeCase)
admin.site.register(WalletAccount)
admin.site.register(WalletTransaction)
admin.site.register(WithdrawalRequest)
