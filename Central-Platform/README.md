# Central Platform (Django)

Central control-plane web app for StayLux, DriveSphere, and Laundrex.

## Implemented
- Modern web admin UI (login, dashboard, tenants, pricing, billing)
- Tenant and module management
- Pricing and commission rule engine
- RBAC foundation:
  - roles
  - permissions
  - tenant memberships
  - membership role assignment
- SSO token APIs (issue + introspect)
- Connector contract APIs (health, tenant sync, usage reports, webhooks)

## Setup
1. `python -m venv .venv`
2. `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py runserver`

## Key URLs
- `/accounts/login/`
- `/`
- `/tenants/`
- `/tenants/agreements/`
- `/pricing/`
- `/billing/`
- `/billing/disputes/`
- `/ops/analytics/`
- `/ops/notifications/`
- `/ops/audit-logs/`
- `/admin/`

## Async Processing (Celery + Redis)
- Worker:
  - `celery -A config worker -l info`
- Beat scheduler:
  - `celery -A config beat -l info`
- Scheduled tasks:
  - `apps.pricing.tasks.reconcile_subscriptions_task`
  - `apps.ops.tasks.process_notifications_task`
  - `apps.connectors.tasks.prune_connector_nonces_task`
  - `apps.ops.tasks.monitor_platform_health_task`

## Health Monitoring
- Command:
  - `python manage.py monitor_platform_health --window-minutes 15`
- Checks:
  - failed notification count in alert window
  - connector failure log count in alert window
- Alert channel:
  - in-app notification (`recipient=ops`)
  - optional email via `OPS_ALERT_EMAIL`

## Two-Factor Auth
- Setup page:
  - `/accounts/2fa/setup/`
- Verify page:
  - `/accounts/2fa/verify/`
- Sensitive permission routes (billing/commission/ops/pricing prefixes) require verified 2FA session.
- Backup codes:
  - Generated on 2FA enable and can be regenerated from setup page.
  - Can be used once in `/accounts/2fa/verify/` if authenticator device is unavailable.
- Admin controls:
  - Force reset 2FA per user.
  - Regenerate backup codes per enabled user.
- Mandatory policy:
  - Superusers and users with configured mandatory permission codes are redirected to 2FA after login.
  - Sensitive action 2FA session expires based on `TWO_FACTOR_PRIVILEGED_SESSION_SECONDS`.

## Versioned API
- Added versioned layer:
  - `/api/v1/connectors/...`
  - `/api/v1/marketplace/...`
  - `/api/v1/health/`
  - `/api/v1/health/ops-summary/`
- Existing routes remain backward-compatible for current clients.

## Observability
- Optional Sentry integration in production:
  - `SENTRY_DSN`
  - `SENTRY_TRACES_SAMPLE_RATE`
  - `SENTRY_ENVIRONMENT`

## Deployment Workflow
- CI workflow:
  - `.github/workflows/ci.yml`
- CD workflow (self-hosted staging/production runners, revision deployment, health verification, and rollback):
  - `.github/workflows/cd.yml`
- Revision rollback script:
  - `scripts/rollback_release.ps1`

## Docker Stack (PostgreSQL + Redis + Web + Celery)
1. `docker compose up --build`
2. Access app at `http://127.0.0.1:8000`

Services in `docker-compose.yml`:
- `db` (PostgreSQL)
- `redis`
- `web` (Django)
- `celery-worker`
- `celery-beat`

## Notification Processing
- Manual retry from UI: `/ops/notifications/`
- Batch processing command:
  - `python manage.py process_notifications --limit 100`
 - Long-running worker:
   - `python manage.py run_ops_worker --interval 30 --limit 100`
 - Windows scheduler setup:
   - `.\scripts\register_notifications_task.ps1`
 - Guide:
 - `docs/ops_worker_setup_windows.md`

## Subscription Reconciliation
- Reconcile command:
  - `python manage.py reconcile_subscriptions --limit 500`
  - optional dry-run: `python manage.py reconcile_subscriptions --limit 500 --dry-run`
- Windows scheduler setup:
  - `.\scripts\register_subscriptions_task.ps1`
- One-time scheduler runner:
  - `.\scripts\run_reconcile_subscriptions_once.ps1 -Limit 500`
- Guide:
  - `docs/subscription_reconcile_setup_windows.md`

## Launch Readiness (Implemented)
- UAT plan:
  - `docs/uat_test_plan.md`
- Production hardening guide:
  - `docs/production_hardening.md`
- Deployment + rollback runbook:
  - `docs/deployment_rollback_runbook.md`

## Operations Scripts
- Preflight checks:
  - `.\scripts\preflight_check.ps1`
- Backup central PostgreSQL and all ready managed tenant databases:
  - `.\scripts\backup_db.ps1`
  - central database only: `.\scripts\backup_db.ps1 -Backend postgresql -CentralOnly`
  - retention override: `.\scripts\backup_db.ps1 -RetentionDays 30`
  - default backup location is outside repo: `%USERPROFILE%\CentralPlatformBackups`

## Connector Secret Rotation
- Supports dual-key grace window:
  - `CONNECTOR_SHARED_SECRET` (active)
  - `CONNECTOR_SHARED_SECRET_NEXT` (next)
- Key version is recorded on connector events and health logs (`active`, `next`, `unsigned`).
- Rotation status command:
  - `python manage.py connector_secret_rotation_status --hours 24`

## Nexivo Demo Requests
- Nexivo submits public demo forms to `POST /api/leads/` through its server route.
- Requests require `X-Nexivo-Timestamp`, `X-Nexivo-Signature`, and `X-Idempotency-Key` headers.
- Set the same strong `NEXIVO_LEAD_SHARED_SECRET` in Nexivo and Central Platform production environments.
- Accepted leads create pending `DemoTenantRequest` records and remain inactive until Central staff approval.
- Central Platform and multi-product interests require staff to choose StayLux, DriveSphere, or Laundrex during approval.
- Approval automatically creates or reuses the owner account and sends a one-time password setup invitation.
- Staff can invite additional owners or members from **Tenants > Manage Users**.
- New memberships remain `invited` until password setup; existing Central accounts become active immediately.
- Restore PostgreSQL DB:
  - `.\scripts\restore_db.ps1 -BackupFile <dump> -DatabaseName <database> -StopApplication -Force`
- Deploy helper:
  - `.\scripts\deploy_release.ps1`
- Go-live orchestrator (backup + deploy + smoke + release log):
  - `.\scripts\go_live.ps1`
  - with HTTP smoke target:
    - `.\scripts\go_live.ps1 -TargetEnvironment production -BaseUrl https://your-domain`
  - with ops notification:
    - `.\scripts\go_live.ps1 -TargetEnvironment production -BaseUrl https://your-domain -Notify`
    - optional: `-NotifyRecipient ops -NotifyChannel in_app`
- Subscription reconcile runner:
  - `.\scripts\run_reconcile_subscriptions_once.ps1 -Limit 500`
- Subscription reconcile scheduler registration:
  - `.\scripts\register_subscriptions_task.ps1 -AtTime "01:15" -Limit 500`

## Tenant Context
- Set active tenant using query string:
  - `?tenant_id=<id>`
- Middleware stores active tenant in session and exposes it in templates.
- Top bar tenant dropdown switches tenant context using:
  - `POST /accounts/switch-tenant/`
- Top bar module chips/dropdown switch module context using:
  - `POST /accounts/switch-module/`
- Module context defaults to `All` when no module is selected.
- Billing, disputes, notifications, audit logs, and analytics honor active module context.
- Billing and marketplace booking operations are blocked until required agreements are accepted.
- Dashboard includes agreement compliance panel with quick resolve links to `/tenants/agreements/?tenant_id=<id>`.

## Phase 2A API Endpoints
- SSO:
  - `POST /accounts/api/sso/token/`
  - `POST /accounts/api/sso/introspect/`
- Connectors:
  - `GET /api/connectors/health/`
  - `POST /api/connectors/tenant/sync/`
  - `POST /api/connectors/usage/report/`
  - `POST /api/connectors/webhooks/events/`
- Commission rules:
  - `GET/POST /pricing/api/commission-rules/`
  - `PATCH/POST /pricing/api/commission-rules/<id>/status/`
- Billing:
  - `POST /billing/api/transactions/`
  - `POST /billing/api/transactions/<id>/refund/`
  - `POST /billing/api/disputes/`
  - `POST /billing/api/disputes/<id>/update/`
  - `POST /billing/payouts/run/`
  - `POST /billing/cash-invoices/generate/`
- Analytics:
  - `GET /ops/api/analytics/metrics/`
  - `GET /ops/api/analytics/export.csv`
- Disputes export:
  - `GET /billing/disputes/export.csv`
  - Supports optional query filters:
    - `tenant_id`, `status`, `reason`, `opened_from`, `opened_to`, `q`
    - `status=pending` maps to `open + under_review`
    - when `status=pending` and no explicit `sort/order` is provided, list defaults to oldest first
    - urgency filter: `priority` (`high|attention|normal`)
    - sorting: `sort` (`opened_at|status|tenant|code`) and `order` (`asc|desc`)
- Dispute urgency:
  - Table shows urgency badges by age for pending disputes:
    - `Normal` (<24h), `Attention` (24h-48h), `High` (>48h)
