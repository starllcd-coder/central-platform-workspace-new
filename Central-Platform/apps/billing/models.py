from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.tenants.models import Module, Tenant


class PaymentTransaction(models.Model):
    PAYMENT_CHANNEL_CHOICES = [
        ("online", "Online"),
        ("cash", "Cash on Arrival"),
    ]
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("refunded", "Refunded"),
        ("cancelled", "Cancelled"),
    ]
    LIFECYCLE_STATE_CHOICES = [
        ("posted", "Posted"),
        ("settled", "Settled"),
        ("refunded", "Refunded"),
        ("cancelled", "Cancelled"),
        ("review", "Review"),
    ]
    SETTLEMENT_STATE_CHOICES = [
        ("pending", "Pending"),
        ("settled", "Settled"),
        ("invoiced", "Invoiced"),
        ("excluded", "Excluded"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="payment_transactions")
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        related_name="payment_transactions",
        null=True,
        blank=True,
    )
    booking_ref = models.CharField(max_length=80)
    idempotency_key = models.CharField(max_length=120, blank=True, default="", db_index=True)
    external_payment_ref = models.CharField(max_length=120, blank=True, default="", db_index=True)
    gateway_txn_ref = models.CharField(max_length=120, blank=True, default="", db_index=True)
    currency = models.CharField(max_length=10, default="OMR")
    payment_channel = models.CharField(max_length=20, choices=PAYMENT_CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="paid")
    lifecycle_state = models.CharField(
        max_length=20, choices=LIFECYCLE_STATE_CHOICES, default="posted"
    )
    settlement_state = models.CharField(
        max_length=20, choices=SETTLEMENT_STATE_CHOICES, default="pending"
    )
    booking_type = models.CharField(max_length=20, default="online")

    gross_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    gateway_fee = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    business_due_for_cash = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    metadata = models.JSONField(default=dict, blank=True)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    reconciliation_note = models.CharField(max_length=255, blank=True)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at", "-id"]
        indexes = [
            models.Index(fields=["tenant", "settlement_state"]),
            models.Index(fields=["booking_ref"]),
            models.Index(fields=["tenant", "idempotency_key"]),
            models.Index(fields=["tenant", "external_payment_ref"]),
        ]

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.booking_ref}:{self.gross_amount}"


class LedgerEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ("payment_received", "Payment Received"),
        ("commission_accrued", "Commission Accrued"),
        ("gateway_fee", "Gateway Fee"),
        ("tax", "Tax"),
        ("payout_sent", "Payout Sent"),
        ("cash_commission_receivable", "Cash Commission Receivable"),
        ("refund", "Refund"),
        ("commission_reversal", "Commission Reversal"),
        ("refund_recovery_due", "Refund Recovery Due"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="ledger_entries")
    transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        related_name="ledger_entries",
        null=True,
        blank=True,
    )
    entry_type = models.CharField(max_length=40, choices=ENTRY_TYPE_CHOICES)
    debit = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    currency = models.CharField(max_length=10, default="OMR")
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.tenant.tenant_code}:{self.entry_type}:{self.debit}/{self.credit}"


class PayoutBatch(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("processing", "Processing"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    code = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code


class Settlement(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("review", "Review"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="settlements")
    payout_batch = models.ForeignKey(
        PayoutBatch,
        on_delete=models.SET_NULL,
        related_name="settlements",
        null=True,
        blank=True,
    )
    source_tx_count = models.PositiveIntegerField(default=0)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=3)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=3)
    net_payout = models.DecimalField(max_digits=12, decimal_places=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tenant.tenant_code} | {self.net_payout}"


class CommissionInvoice(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="commission_invoices")
    code = models.CharField(max_length=40, unique=True)
    amount_due = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="OMR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    due_date = models.DateField()
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code}:{self.tenant.tenant_code}"


class RefundRecord(models.Model):
    REFUND_TYPE_CHOICES = [
        ("full", "Full"),
        ("partial", "Partial"),
    ]
    STATUS_CHOICES = [
        ("processed", "Processed"),
        ("review", "Review"),
    ]

    transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.CASCADE,
        related_name="refund_records",
    )
    refund_type = models.CharField(max_length=20, choices=REFUND_TYPE_CHOICES)
    refund_percent = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    customer_refund_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    commission_reversal_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    business_recovery_amount = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="processed")
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"RR-{self.id}:{self.transaction.booking_ref}:{self.customer_refund_amount}"


class DisputeCase(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("under_review", "Under Review"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]
    REASON_CHOICES = [
        ("refund_delay", "Refund Delay"),
        ("wrong_charge", "Wrong Charge"),
        ("service_issue", "Service Issue"),
        ("other", "Other"),
    ]
    RESOLUTION_CHOICES = [
        ("refund", "Refund"),
        ("partial_refund", "Partial Refund"),
        ("no_action", "No Action"),
        ("adjustment", "Adjustment"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="disputes")
    transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        related_name="disputes",
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=40, unique=True)
    reason = models.CharField(max_length=30, choices=REASON_CHOICES, default="other")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    resolution_type = models.CharField(
        max_length=30, choices=RESOLUTION_CHOICES, blank=True, default=""
    )
    resolution_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_disputes",
    )
    resolved_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_disputes",
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-opened_at"]

    def __str__(self):
        return f"{self.code}:{self.status}"


class WalletAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("platform", "Platform"),
        ("tenant", "Tenant"),
    ]
    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
    ]

    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name="wallet_account",
        null=True,
        blank=True,
    )
    currency = models.CharField(max_length=10, default="OMR")
    available_balance = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["account_type", "tenant_id"]

    def __str__(self):
        if self.account_type == "platform":
            return "Platform Wallet"
        return f"Tenant Wallet:{self.tenant.tenant_code if self.tenant else 'n/a'}"


class WalletTransaction(models.Model):
    TX_TYPE_CHOICES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
    ]
    REASON_CHOICES = [
        ("commission_accrual", "Commission Accrual"),
        ("settlement_credit", "Settlement Credit"),
        ("withdrawal_debit", "Withdrawal Debit"),
        ("adjustment", "Adjustment"),
    ]

    wallet = models.ForeignKey(
        WalletAccount,
        on_delete=models.CASCADE,
        related_name="wallet_transactions",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        related_name="wallet_transactions",
        null=True,
        blank=True,
    )
    payment_transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        related_name="wallet_transactions",
        null=True,
        blank=True,
    )
    settlement = models.ForeignKey(
        Settlement,
        on_delete=models.SET_NULL,
        related_name="wallet_transactions",
        null=True,
        blank=True,
    )
    tx_type = models.CharField(max_length=20, choices=TX_TYPE_CHOICES)
    reason = models.CharField(max_length=40, choices=REASON_CHOICES, default="adjustment")
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    balance_after = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.wallet_id}:{self.tx_type}:{self.amount}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("paid", "Paid"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="withdrawal_requests")
    wallet = models.ForeignKey(
        WalletAccount,
        on_delete=models.PROTECT,
        related_name="withdrawal_requests",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    currency = models.CharField(max_length=10, default="OMR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    notes = models.CharField(max_length=255, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_withdrawals",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_withdrawals",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at", "-id"]

    def __str__(self):
        return f"WD-{self.id}:{self.tenant.tenant_code}:{self.amount}:{self.status}"
