# Cross-Platform Go-Live Checklist

## 1. Production Environment Finalization
- Set strong secrets and URLs:
  - Central Platform: `DJANGO_SECRET_KEY`, `CONNECTOR_SHARED_SECRET`
  - DriveSphere/Laundrex/StayLux: `CENTRAL_CONNECTOR_SECRET`, `CENTRAL_PLATFORM_URL`, `CENTRAL_TENANT_CODE`
  - Nexivo websites: `NEXT_PUBLIC_CENTRAL_PLATFORM_API`
- Ensure `DJANGO_ALLOWED_HOSTS` contains real domain names (not localhost).
- Ensure production endpoints use HTTPS.

## 2. Real Credential Validation
- Create production-ready test users:
  - customer user for `/api/auth/login/`
  - provider user for `/api/provider/login/`
- Validate:
  - successful customer login
  - successful provider login
  - failed login with bad credentials (401)

## 3. Cross-System End-to-End Smoke
- Start/verify Central Platform.
- Run:
  - `.\scripts\verify-central-connectivity.ps1 -CentralBaseUrl https://<central-domain> -ConnectorSecret <secret> -RunConnectorPush`
- Confirm:
  - `/api/health/` OK
  - `/api/connectors/health/` OK
  - `/api/platform/tenants/` returns active tenants
  - connector push succeeds for DriveSphere, Laundrex, StayLux

## 4. Security Hardening
- Rotate all `dev-*` secrets before production.
- Enable signed connector requests:
  - Central: `CONNECTOR_REQUIRE_SIGNED_REQUESTS=1`
  - Apps: `CENTRAL_CONNECTOR_SIGNED=1`
- Enable secure cookies and SSL redirect in production.
- Keep CORS/hosts restricted to deployed domains.

## 5. Monitoring and Alerting
- Enable error tracking (`SENTRY_DSN`) where configured.
- Configure operations alert routing (`OPS_ALERT_EMAIL` or equivalent).
- Add periodic health checks for:
  - Central `/api/health/`
  - Connector health endpoint
  - Website critical API routes (`/api/auth/login/`, `/api/payments/session/`)
- Record the run date/time and owner for each smoke pass.
