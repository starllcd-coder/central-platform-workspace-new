# Subscription Reconciliation Setup (Windows)

This guide schedules daily subscription lifecycle reconciliation.

## What it does
- Cancels expired `TenantSubscription` rows (`trial`/`active` with `end_date < today`)
- Syncs tenant-level `subscription_status`
- Writes audit logs (`pricing.subscription.expired`)
- Appends run output to:
  - `release_logs/subscription_reconcile.log`

## One-time run
```powershell
.\scripts\run_reconcile_subscriptions_once.ps1 -Limit 500
```

Dry-run:
```powershell
.\scripts\run_reconcile_subscriptions_once.ps1 -Limit 500 -DryRun
```

## Register daily scheduled task
Default (daily at `01:15`):
```powershell
.\scripts\register_subscriptions_task.ps1
```

Custom time and limit:
```powershell
.\scripts\register_subscriptions_task.ps1 -AtTime "02:30" -Limit 1000
```

Dry-run task registration:
```powershell
.\scripts\register_subscriptions_task.ps1 -TaskName "CentralPlatform-ReconcileSubscriptions-DryRun" -DryRun
```

## Manual command equivalent
```powershell
.\.venv\Scripts\python.exe manage.py reconcile_subscriptions --limit 500
```

Dry-run:
```powershell
.\.venv\Scripts\python.exe manage.py reconcile_subscriptions --limit 500 --dry-run
```
