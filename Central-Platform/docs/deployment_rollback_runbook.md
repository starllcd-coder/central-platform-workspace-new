# Deployment and Rollback Runbook

## Pre-Deploy Checklist
1. Confirm UAT sign-off (`docs/uat_test_plan.md`).
2. Ensure production backup exists for current day.
3. Confirm access to production server and env file.
4. Confirm rollback owner is available.

## Standard Deployment (Windows)
Use:

```powershell
.\scripts\deploy_release.ps1
```

What it does:
1. Runs preflight checks.
2. Creates timestamped PostgreSQL backups for central and managed tenant databases.
3. Applies Django migrations.
4. Runs post-deploy check.

## Recommended Go-Live Command
For release day, prefer the orchestrator:

```powershell
.\scripts\go_live.ps1 -TargetEnvironment production -BaseUrl https://your-domain
```

This performs:
1. Deploy sequence (preflight + backup + migrate + checks)
2. Smoke checks
3. Timestamped release log in `release_logs/`
4. Optional ops notification:
   - `.\scripts\go_live.ps1 -TargetEnvironment production -BaseUrl https://your-domain -Notify`

## Manual Deployment Steps
If you need manual control:
1. `.\scripts\preflight_check.ps1`
2. `.\scripts\backup_db.ps1`
3. `.\.venv\Scripts\python.exe manage.py migrate --noinput`
4. `.\.venv\Scripts\python.exe manage.py check`
5. Restart application process/service.

## Post-Deploy Validation (5-10 minutes)
1. Login at `/accounts/login/`.
2. Open dashboard and verify KPI cards load.
3. Open billing and disputes pages.
4. Trigger a small notification and verify worker processing.
5. Validate analytics endpoint:
   - `/ops/api/analytics/metrics/`

## Rollback Triggers
Rollback immediately for:
- production outage
- login failure spike
- billing/dispute flow breakage
- data integrity risk

## Rollback Procedure (PostgreSQL)
1. Stop app process.
2. Restore latest known-good DB backup:
   - `.\scripts\restore_db.ps1 -BackupFile <dump> -DatabaseName <database> -StopApplication -Force`
3. Revert code to previous release package/tag.
4. Start app process.
5. Run smoke checks (login, dashboard, billing).

## Incident Log Template
Capture:
- start/end time
- release identifier
- detected issue
- rollback decision owner
- root cause summary
- corrective actions
