# Production Hardening Guide

## 1. Environment and Secrets
1. Use a dedicated production `.env` file.
2. Set `DEBUG=False`.
3. Set strong `SECRET_KEY`.
4. Restrict `ALLOWED_HOSTS` to production domains.
5. Store credentials outside source control.

## 2. Transport Security
1. Terminate TLS using trusted certificates.
2. Redirect all HTTP traffic to HTTPS.
3. Enforce secure cookies at proxy/app level.

## 3. Access Control and Admin Safety
1. Keep super admin accounts minimal.
2. Enable strong passwords and periodic rotation.
3. Restrict admin panel access by network/IP when possible.
4. Remove inactive user accounts.

## 4. Database and Backups
Production uses PostgreSQL. The backup script inventories the central database and all ready managed PostgreSQL tenant databases.

1. Use daily automated backup and copy the timestamped directory to encrypted off-host storage:
   - `.\scripts\backup_db.ps1`
2. Keep backup retention (for example 14-30 days).
3. Test restore weekly in non-production using:
   - `.\scripts\restore_db.ps1 -BackupFile <dump> -DatabaseName <database> -StopApplication -Force`
4. Verify each manifest SHA-256 before restoration and store at least one encrypted off-machine copy.
5. Record the restore duration and recovered timestamp against the agreed RTO and RPO.

## 5. Runtime Health Checks
Before each deploy run:
- `.\scripts\preflight_check.ps1`

This validates:
- venv/python path
- Django system checks
- pending migrations visibility

## 6. Job Reliability (Notifications)
1. Keep notification task/worker active:
   - Scheduled task or process manager.
2. Monitor failed notification count from `/ops/notifications/`.
3. Define alert threshold for repeated failures.

## 7. Logging and Audit
1. Keep application stdout/stderr logs for deployment troubleshooting.
2. Review `/ops/audit-logs/` regularly.
3. Preserve logs during incidents for postmortem.

## 8. Monitoring Baseline
Track at minimum:
- app availability
- login success/failure trend
- dispute backlog and high-priority aging
- notification failed queue size

## 9. Security Patch Routine
1. Monthly dependency review.
2. Apply Django/Python security patches in staging first.
3. Re-run UAT smoke tests after patching.
