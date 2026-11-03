# Workspace Integration Map

## Repos and Roles
- `StayLux`: hospitality product suite (web + mobile + desktop + owner admin).
- `Laundrex`: laundry operations suite (Django + mobile + desktop).
- `DriveSphere`: vehicle rental suite (web + mobile + desktop).
- `Nexivo`: public websites (booking + business marketing/onboarding).
- `Central-Platform`: control plane for tenancy, billing, commission, agreements, connectors, and shared public API.

## Current Technical Reality
- `Central-Platform` already provides:
  - SSO issue/introspect APIs.
  - Connector APIs (`health`, `tenant/sync`, `usage/report`, `webhooks/events`).
  - Billing/commission/tenant agreement logic.
- `Nexivo` expects public endpoints under `NEXT_PUBLIC_CENTRAL_PLATFORM_API` for:
  - auth, listings, tenants, bookings, leads/onboarding.
- `StayLux` has `sync_engine` and can be integrated as a connector producer.
- `Laundrex` has cloud sync primitives (`sync_with_cloud`) and sync settings.
- `DriveSphere` has multi-client architecture and is ready for connector integration events.

## Implemented in This Change
- Added a new public API bridge in `Central-Platform` under `/api/`:
  - `GET /api/health/`
  - `GET /api/platform/tenants/`
  - `GET /api/tenants/`
  - `GET /api/listings/`
  - `POST /api/bookings/`
  - `POST /api/auth/login/`
  - `POST /api/auth/register/`
  - `GET /api/customer/profile/`
  - `GET /api/customer/bookings/`
  - `GET /api/customer/summary/`
  - `POST /api/leads/`
  - `POST /api/business/onboarding/`
  - `POST /api/provider/login/`
- These endpoints map into existing central data models and connector event logging.

## Integration Contract (All App Backends -> Central)
- Base URL: `<CENTRAL_PLATFORM_BASE_URL>`
- Connector header:
  - `X-Connector-Secret: <CONNECTOR_SHARED_SECRET>`
- Optional signed request headers (recommended for production):
  - `X-Connector-Timestamp`
  - `X-Connector-Signature` (HMAC-SHA256 of `<timestamp>.<raw_body>`)
- Use:
  - `POST /api/connectors/tenant/sync/` when tenant/module state changes.
  - `POST /api/connectors/usage/report/` for daily/monthly usage aggregation.
  - `POST /api/connectors/webhooks/events/` for domain events (booking/payment/etc).
  - `POST /accounts/api/sso/introspect/` to validate central-issued SSO tokens.

## Recommended Rollout Order
1. Point Nexivo env `NEXT_PUBLIC_CENTRAL_PLATFORM_API` to Central `/api`.
2. Enable and verify marketplace tenant/module flags in Central.
3. Wire StayLux backend to connector endpoints for booking + usage events.
4. Wire Laundrex backend sync/ops events to connector endpoints.
5. Wire DriveSphere backend sync/ops events to connector endpoints.
6. Enable signed connector requests and stricter gateway checks in production.

## Validation Checklist
- `GET /api/health/` returns `status=ok`.
- Nexivo tenant/listing pages load using central API.
- Nexivo booking submission creates:
  - Stay booking rows for StayLux listings (when unit is available).
  - Connector events for all modules.
- Each app backend can call central connector endpoints with auth header.
- Central ops pages show connector activity and events.

## Connector Commands (Per App)
- StayLux (`StayLux/web`):
  - `python manage.py push_central_connector --kind tenant --tenant-code <TNT_CODE>`
  - `python manage.py push_central_connector --kind usage --tenant-code <TNT_CODE>`
  - `python manage.py push_central_connector --kind event --tenant-code <TNT_CODE> --event-name booking.updated`
- Laundrex (`Laundrex`):
  - `python manage.py push_central_connector --kind tenant --tenant-code <TNT_CODE>`
  - `python manage.py push_central_connector --kind usage --tenant-code <TNT_CODE>`
  - `python manage.py push_central_connector --kind event --tenant-code <TNT_CODE> --event-name order.updated`
- DriveSphere (`DriveSphere/web`):
  - `python manage.py push_central_connector --kind tenant --tenant-code <TNT_CODE>`
  - `python manage.py push_central_connector --kind usage --tenant-code <TNT_CODE>`
  - `python manage.py push_central_connector --kind event --tenant-code <TNT_CODE> --event-name booking.updated`

## Required Env Keys (App Backends)
- `CENTRAL_PLATFORM_URL` (default local: `http://127.0.0.1:8000`)
- `CENTRAL_CONNECTOR_SECRET` (must match central `CONNECTOR_SHARED_SECRET`)
- `CENTRAL_CONNECTOR_SIGNED` (`1` to enable signed connector payloads)
- `CENTRAL_TENANT_CODE` (tenant identity in central)
- `CENTRAL_MODULE_CODE` (`staylux`, `laundrex`, or `drivesphere`)
