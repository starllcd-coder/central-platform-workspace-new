# Central Platform Production Readiness Audit

Date: 2026-06-28  
Scope: Central Platform Django application, local deployment assets, security controls, data safety, automated tests, and operations controls. Real external-provider connectivity was excluded, but integration boundaries and failure behavior were reviewed.  
Decision: **CONDITIONAL NO-GO - repository remediation complete; staging evidence pending**

## Remediation Update - 2026-06-29

All findings that can be resolved and verified within this repository have been addressed:

- PR-001: Fixed. Every internal payment API now requires timestamped HMAC authentication with a single-use database nonce.
- PR-002: Fixed. Gateway webhooks fail closed for missing secrets, signatures, timestamps, stale requests, and disabled providers.
- PR-003: Fixed. Payment finalization uses row locking and terminal-state checks; webhook events and tenant idempotency keys have database uniqueness constraints.
- PR-004: Implemented. Backup and restore tooling now supports the central PostgreSQL database and ready managed tenant databases, with manifests and SHA-256 hashes. A real restore drill is still required in staging.
- PR-005: Fixed. Positive finite payment/refund amounts and remaining refundable balance are enforced in services and database constraints.
- PR-006: Fixed in Compose. Redis is no longer published, requires authentication, persists data, and has a health check.
- PR-007: Fixed. Production Django cache and cross-process rate-limit state use authenticated Redis.
- PR-008: Fixed in settings. HTTPS redirect, proxy awareness, secure cookies, one-year HSTS, subdomains, and preload are enabled. Real TLS/proxy behavior remains a staging check.
- PR-009: Fixed in deployment assets. Containers run non-root/read-only with dropped capabilities, resource limits, health dependencies, one-shot migration ownership, and explicit image pins. Image build could not be executed because Docker Desktop was not running.
- PR-010: Fixed. Gateway API and webhook secrets are encrypted at rest and hidden behind password inputs in admin.
- PR-011: Fixed. Direct dependencies and build tools are pinned, CI runs tests and `pip-audit`, and the local scan reports no known vulnerabilities.
- PR-012: Fixed. Django was upgraded from 5.2.14 to 5.2.15.
- PR-013: Improved. The suite increased from 58 to 67 passing tests with payment authorization, replay, idempotency, refund, webhook, encryption, and retention coverage. Browser, accessibility, load, failover, and staging recovery tests remain environment-dependent gates.

Verification completed on 2026-06-29:

- Full test suite: 73/73 passed.
- `manage.py check --deploy`: no issues.
- `makemigrations --check --dry-run`: no changes detected.
- `pip check`: no broken requirements.
- `pip-audit --local`: no known vulnerabilities.
- `docker compose config --quiet`: passed with audit-only placeholders.
- Backup and restore PowerShell scripts: parser validation passed.

The Nexivo demo-request integration was subsequently completed: the website form now submits validated data through a signed and idempotent server route, Central creates a pending approval record and connector audit event, and multi-product requests require staff module selection.

Secure business account onboarding was also completed: demo approval and staff-created tenants can create or reuse owner accounts, tenant memberships remain invited until one-time password setup, existing accounts are activated without password replacement, and staff can invite additional tenant users from the UI.

Remaining release gates are operational evidence, not unresolved source findings: build and start the containers, migrate a production-like PostgreSQL database, perform and time a backup/restore drill including a tenant database, verify TLS/HSTS and SMTP/alerts, execute critical browser journeys, and complete load/failover testing.

## Executive Summary

The application has a solid functional baseline: all 58 automated tests pass, migrations are consistent, installed dependencies have no resolver conflicts, production mode rejects known development secrets, secure cookies are enabled, privileged permissions support 2FA and reauthentication, connector requests support signatures and replay protection, and demo tenants are blocked from live financial and connector operations.

Production release is blocked by unauthenticated financial mutation endpoints, fail-open payment webhook verification, non-idempotent payment finalization, and a backup/restore process that only supports SQLite while the production deployment uses PostgreSQL. Deployment hardening, distributed rate limiting, dependency reproducibility, and staging evidence are also incomplete.

## Release Blockers

### PR-001 - Critical - Financial APIs do not require authentication or authorization

Evidence: `apps/paymentsvc/views.py:49`, `:67`, `:87`, `:116`, `:128`, and `:143` expose payment creation, verification, refund, status, card guarantee, and extension payment operations without login, service authentication, tenant authorization, or a signed internal-request check. Mutation endpoints are also CSRF-exempt.

Impact: An unauthenticated caller can create payment records for arbitrary tenant IDs, invoke verification, request refunds, and retrieve payment details when a payment ID is known.

Required remediation:

- Require signed service authentication with timestamp, nonce, and key rotation for machine APIs.
- Enforce tenant scope and operation-specific permissions.
- Separate public checkout initiation from privileged verify/refund operations.
- Add deny-path and cross-tenant authorization tests.

### PR-002 - Critical - Payment webhook verification fails open

Evidence: `apps/paymentsvc/services.py:233-234` returns a valid signature result when no gateway secret is configured.

Impact: A missing or deleted gateway secret turns every submitted webhook signature into a valid signature. A forged payment-success webhook can trigger financial state changes.

Required remediation:

- Fail closed when a provider is disabled, absent, or has no webhook secret.
- Reject stale timestamps and replayed webhook event IDs.
- Add production startup checks requiring secrets for every enabled provider.

### PR-003 - Critical - Payment finalization and webhooks are not idempotent

Evidence: `apps/paymentsvc/services.py:157-181` creates a new `PaymentTransaction` whenever verification reports success, without returning early for an already-captured payment. `PaymentWebhookLog.event_id` at `apps/paymentsvc/models.py:121` is indexed but not unique. Payment idempotency keys at `apps/paymentsvc/models.py:67` are also indexed but not protected by a tenant-scoped database uniqueness constraint.

Impact: Repeated verify calls, duplicate webhooks, concurrent requests, or retries can create duplicate accounting transactions and ledger entries.

Required remediation:

- Lock the payment row and make captured state terminal for finalization.
- Add tenant-scoped conditional uniqueness for non-empty idempotency keys.
- Add provider/event ID uniqueness and duplicate-event handling.
- Add concurrent and repeated-delivery tests.

### PR-004 - High - Production PostgreSQL has no implemented backup/restore path

Evidence: `docker-compose.yml` deploys PostgreSQL, while `scripts/backup_db.ps1:13`, `scripts/restore_db.ps1:17`, and `docs/production_hardening.md:22` only handle `db.sqlite3`.

Impact: The documented go-live and rollback process cannot back up or restore the production database. Recovery point and recovery time objectives are untested.

Required remediation:

- Implement encrypted `pg_dump`/`pg_restore` automation and off-host retention.
- Include all tenant databases in the inventory and backup schedule.
- Perform and record a staging restore drill before release.
- Define RPO, RTO, retention, ownership, and restore authorization.

## High And Medium Findings

### PR-005 - High - Refund and amount integrity constraints are incomplete

`create_payment()` does not enforce a positive amount. `refund_payment()` does not reject zero, negative, or over-payment refunds before calling the adapter. Database check constraints do not enforce these invariants.

### PR-006 - High - Redis is published without application-configured authentication

`docker-compose.yml:19` publishes port 6379 and uses unauthenticated Redis URLs. Remove the host port unless operationally required, add Redis ACL/authentication, and restrict network access. Redis documentation recommends access only from trusted application clients.

### PR-007 - High - Rate limiting and alert deduplication use per-process memory

No production `CACHES` setting is configured, so Django uses per-process local-memory cache. API rate counters and health-alert suppression are therefore independent across three Gunicorn workers and other processes. Configure the existing Redis service as the shared Django cache with a dedicated authenticated namespace.

### PR-008 - Medium - HTTPS enforcement is incomplete in the repository

`manage.py check --deploy` reports `security.W004` and `security.W008`: no HSTS and no application-level SSL redirect. A reverse proxy may own these controls, but no proxy/TLS configuration or verification evidence is present. Configure and test proxy-aware HTTPS, trusted proxy headers, redirects, and staged HSTS rollout.

### PR-009 - Medium - Containers and orchestration lack production hardening

The image runs as root, services have no health checks, startup uses `depends_on` without readiness conditions, database migrations run automatically in every web startup command, and images use floating major tags. Add a non-root runtime user, health/readiness checks, immutable image references, resource limits, restart-safe migration ownership, and restricted container capabilities.

### PR-010 - Medium - Gateway secrets are stored as plaintext model fields

`GatewayConfig.secret_key` and `GatewayConfig.webhook_secret` are ordinary character fields. Store provider secrets in a managed secret store or encrypt them with an independently managed key, and prevent secret display in admin and logs.

### PR-011 - Medium - Builds are not reproducible and vulnerability automation is absent

`requirements.txt` uses broad version ranges without a lock file or hashes. `pip check` passes, but `pip-audit` is not installed and no CI vulnerability scan was found. Pin reviewed versions, generate hashes, and run dependency and container-image scans in CI.

### PR-012 - Low - Installed Django patch is behind a security release

The environment has Django 5.2.14. Django 5.2.15, released 2026-06-03, fixes five low-severity security issues in 5.2.14. Upgrade and rerun the suite. Source: https://docs.djangoproject.com/en/5.2/releases/5.2.15/

### PR-013 - Medium - Automated coverage is insufficient for production claims

The 58 tests cover important workflows but do not establish broad authorization matrices, payment abuse cases, concurrent financial operations, browser journeys, accessibility, load/capacity behavior, PostgreSQL migration behavior, worker recovery, or backup restoration. Add these as release-gate suites.

## Verified Passes

- Full Django suite: 58/58 tests passed.
- Django system check during tests: no issues.
- Migration consistency: `makemigrations --check --dry-run` reported no changes.
- Installed dependency compatibility: `pip check` reported no broken requirements.
- Production mode uses `DEBUG=False` and secure session/CSRF cookies.
- Production startup rejects known default application, connector, marketplace, and encryption secrets.
- Privileged permission paths support mandatory 2FA and recent reauthentication.
- Tenant context checks membership before accepting tenant or module selection.
- Connector APIs include signatures, timestamp skew checks, replay nonce protection, rotation support, rate-limit headers, and demo-tenant blocking.
- Sentry integration and structured console logging exist.
- Health endpoint checks database and cache availability.
- Docker Compose syntax reached environment loading; full resolution was blocked because the deployment `.env` is intentionally absent from this workspace.

## Unverified External Evidence

- No production-like staging environment or PostgreSQL instance was supplied.
- No real production `.env`, TLS proxy, DNS, certificate, SMTP, SMS, gateway, or connector credentials were inspected.
- No load, soak, browser, accessibility, penetration, failover, worker-kill, or restore drill was executed.
- No production logs, alert delivery records, dashboards, RPO/RTO records, or incident exercises were available.
- Dependency CVE scanning could not run because `pip-audit` is not installed.

## Release Gate

Production approval requires PR-001 through PR-004 to be fixed and independently retested. PR-005 through PR-011 should be closed or explicitly accepted by accountable owners with compensating controls and expiry dates. A production-like staging run must then demonstrate PostgreSQL migration, backup restoration, HTTPS behavior, shared-cache rate limiting, background-worker recovery, and end-to-end critical business workflows.

Reference guidance:

- Django deployment checklist: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- Django cache guidance: https://docs.djangoproject.com/en/5.2/topics/cache/
- Redis security guidance: https://redis.io/docs/latest/operate/oss_and_stack/management/security/
