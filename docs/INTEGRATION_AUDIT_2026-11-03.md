# Cross-application integration audit

Date: 3 November 2026 (Asia/Dubai).

## Verdict and scope

The workspace is **not fully connected end to end**. Central has useful control-plane and marketplace APIs, and Nexivo calls several of them, but critical provider connections are missing. This was a source and local test audit across all five repositories, including mobile/desktop configuration. It is not certification of deployed services or every application feature. No production URLs, accounts, infrastructure, or deployment settings were validated. Application source was left unchanged; this report is the audit deliverable.

| Connection | Evidence-based status |
|---|---|
| StayLux → Central | Missing Central-specific connector settings, client, and push command in this checkout. Existing local/cloud sync uses a separate contract. |
| Central → StayLux | Missing `/api/central/bookings/` receiver expected by Central. |
| DriveSphere → Central | Manual tenant/usage/event command exists; signed requests are incompatible with Central's nonce contract. |
| Central → DriveSphere | Expected `/api/central/bookings/` does not resolve in Django. |
| Laundrex → Central | Manual signed tenant/usage/event command exists. No automatic Central publishing found. |
| Central → Laundrex | Signed, tenant-aware order receiver exists. Actual cross-service order creation remains untested. |
| Nexivo ↔ Central | Real listing, booking, customer authentication/profile/history, provider login and signed demo-lead paths exist. Several other features remain static or incomplete. |

## Blocking findings

### 1. StayLux Central bridge is absent

Central's `apps/connectors/management/commands/dispatch_marketplace_bookings.py` targets `/api/central/bookings/` for StayLux. `StayLux/web/api/urls.py` contains no such route. Searching StayLux Python and Dart sources found no Central client, Central connector settings, `push_central_connector` command, or Central SSO introspection call. The existing `sync_engine` has its own push/pull/ingest routes and configuration; it does not implement Central's documented contract.

Required: implement a tenant-aware signed bridge, an idempotent booking receiver using StayLux booking/availability rules, and inventory/usage/status publication. Update `Central-Platform/docs/workspace_integration_map.md`, which incorrectly lists an implemented StayLux push command.

### 2. DriveSphere cannot receive dispatched marketplace bookings

Central targets `/api/central/bookings/`. DriveSphere's API URL configuration contains no receiver; a local Django URL resolver check raised `Resolver404` for that exact path. Existing internal booking endpoints require a different authentication/request contract and are not a replacement by URL alone.

Required: implement the signed, tenant-aware receiver with resource mapping, availability checks, idempotency, and a positive acknowledgement only after booking persistence.

### 3. DriveSphere signed outbound requests fail Central authentication

`DriveSphere/web/apps/core/central_connector.py` signs `<timestamp>.<body>` and sends no nonce. `Central-Platform/apps/connectors/views.py::_extract_request_security` requires `X-Connector-Nonce` and verifies `<timestamp>.<nonce>.<body>`. Production Central requires signed requests. Thus enabling signing in DriveSphere does not fix this connection; the protocol must change.

Required: use a fresh nonce and the Central signature format. Laundrex's outbound client already uses this format. Add a real client-to-Central contract test.

### 4. Marketplace prices are trusted from the browser

`Central-Platform/apps/marketplace/views.py::submit_booking_api` takes `estimatedTotal` or `total` from the payload and checks only that the parsed amount is positive. This permits a changed browser request to supply a lower booking amount. Nexivo's stay form fixes `nights = 1`; its car form fixes `rentalDays = 1`, irrespective of chosen dates.

Required: calculate authoritative prices on the server from resource, dates, quantity, currency, taxes and applicable rules; validate finite amounts and date ranges. Make UI estimates use the same quote contract. Do this before enabling paid bookings.

### 5. Payments and card guarantees are incomplete

Nexivo booking forms contain placeholder card inputs and submit directly to booking routes, then redirect to customer history. There is no completed hosted checkout/tokenization flow there. Central's public `payment_session_api` creates a signed token and a relative checkout URL; it does not create a live gateway session. `apps/paymentsvc/services.py::build_adapter` explicitly rejects non-mock modes other than disabled; adapters generate mock checkout URLs.

Required: implement an actual gateway adapter, hosted checkout/card tokenization, verified webhooks, booking/payment linkage, refunds and reconciliation. Ensure provider dispatch follows the intended payment/guarantee policy. Keep online payment unavailable until this works end to end.

## Other missing or misleading integration behavior

### 6. Inventory and lifecycle synchronization are not automatic

DriveSphere and Laundrex call `post_connector` only from manual management commands in the scanned Python source. These commands send tenant state, aggregate usage or a latest-record event; they do not publish resource inventories, rates or availability. Central's generic webhook receiver logs accepted events; it does not apply booking lifecycle updates to `MarketplaceBooking`.

Required: add transactional outbound queues and workers for inventory, availability, rates, bookings/orders, cancellations and relevant payment events. Implement consumers that apply versioned, idempotent updates. Preserve stable provider resource IDs across Central listings and app records. Configure scheduling and retry monitoring.

### 7. Nexivo status screens overstate connection health

`nexivo/src/app/api/central/route.ts` marks every non-planned connector connected after only health, tenants and listings requests succeed. This does not test identity, pricing, billing, notifications, analytics or privacy. The connector catalog contains static mock statuses and illustrative endpoints. `isLaunchReadyConnector` treats mock connectors as launch ready.

Required: replace inferred/static status with capability-specific probes and last-success/error information. Never count a mock integration as production readiness.

### 8. Nexivo partner/admin dashboards use static datasets

`src/app/partner/page.tsx` imports bookings, invoices, listings and reports from `partner-dashboard-data`. `src/app/admin/page.tsx` imports metrics, monitoring and analytics from `admin-data`. Authentication gates exist, but these dashboards do not represent actual Central operational data.

Required: replace datasets with authenticated, tenant-scoped Central APIs and proper loading/error/empty states. Audit the customer rewards, documents, favorites, notifications and related screens before advertising them as synchronized features.

### 9. Nexivo's generic sync route is not a sync implementation

`src/app/api/central/sync/route.ts` posts arbitrary sync content to Central `/leads/`, without the signatures required by Central's demo-lead contract. It falls back to `mockCentralPlatformSync` when mocks are allowed. In contrast, `/api/leads/demo-request` validates and signs leads correctly.

Required: remove the misleading generic sync route or replace it with a properly authenticated, explicitly defined synchronization API. Keep sales leads and domain synchronization separate.

### 10. Mock fallbacks can conceal failed operations

Nexivo defaults to allowing mock fallback outside production; the environment can also enable it explicitly. Booking routes can return invented booking references after Central errors, and listing reads can show sample inventory. With fallback disabled, booking routes turn all Central failures, including validation or availability errors, into a generic 502. Customer history catches all upstream errors and returns an empty list.

Required: explicitly disable fallback in deployed environments, clearly identify demo mode, preserve actionable upstream error codes, and display failed history loads distinctly from no bookings.

### 11. Password recovery and cross-app SSO are unfinished

`ForgotPasswordForm` has no submission handler, API action, or named email input. Central issues SSO tokens, but no Central SSO introspection calls were found in the three app backends. Nexivo's Central-backed login does not by itself establish shared sessions across the provider apps. Booking UI text promises automatic account creation, while the submit flow does not create a Nexivo session and redirects guests into protected customer pages.

Required: wire password recovery, define account linking and SSO policy, and provide a clear authenticated or guest booking confirmation/retrieval flow.

### 12. Mobile/desktop deployment targets require alignment

DriveSphere customer mobile defaults to `http://127.0.0.1:8000/api`, while staff mobile defaults to a Railway demo URL under `/api/v1`. StayLux mobile defaults to local `/api/mobile`; owner admin uses platform-specific localhost/emulator defaults. These are source defaults, not proof of what released builds use. Desktop and local/cloud synchronization do not establish a Central connection automatically.

Required: verify each release's API overrides, tenant identity and environment against its own product backend. Provider mobile apps should use their product APIs; those backends should bridge to Central. Do not replace all product API URLs with Central, whose API contract differs.

### 13. Existing connectivity checks and documentation need replacement

`scripts/verify-central-connectivity.ps1` hardcodes another computer's `C:\Users\LENOVO\Desktop\Central_Platform_Workspace` paths, assumes absent per-project virtual environments, defaults to a development secret, omits signed-mode setup and checks only health/listing endpoints plus optional manual tenant pushes. That cannot establish full connectivity. The integration map claims StayLux functionality absent from this checkout.

Required: resolve project paths relative to the script, require explicit configuration for mutations, and add read-only preflight plus a controlled test-tenant end-to-end suite. Check persisted provider records and return status updates, not only HTTP acceptance.

### 14. Dispatch recovery needs a crash-recovery path

Central's dispatcher claims an event by changing its status to `dispatching`; subsequent selection only includes `accepted` and `dispatch_failed`. A process exit after claiming can leave the booking permanently excluded from retries.

Required: add a claim lease and stale-claim recovery, with provider idempotency so uncertain deliveries can safely be retried.

## Local validation performed

| Check | Result | Limit |
|---|---|---|
| Central `python manage.py test apps.connectors apps.marketplace --noinput` | 21 tests passed | Dispatch tests mock HTTP provider acknowledgements; they do not exercise missing app receivers. |
| Central `python manage.py test apps.paymentsvc --noinput` | 11 tests passed | Mock service/security behavior, not live payment processing. |
| DriveSphere `python manage.py check` | Passed | Framework configuration check only. |
| DriveSphere resolve `/api/central/bookings/` | Failed: `Resolver404` | Confirms missing inbound route. |
| Laundrex `python manage.py test apps.orders.tests_connector --noinput` | 1 test passed | Signature/tenant/replay helper test; no persisted order or full HTTP delivery. |
| StayLux `python manage.py check` | Blocked by missing installed `openpyxl` | Dependency is declared in requirements; this is a local environment gap. Other issues may surface once dependencies are installed. |
| Nexivo build/typecheck and Flutter builds | Not run | Node/npm not found on PATH; no installed Nexivo dependencies found in inspected project root. Mobile releases were inspected statically. |

No deployed environment values were read or verified. No production data was changed and no tenant sync commands were sent.

## Recommended implementation order

1. Complete StayLux and DriveSphere booking receivers and fix DriveSphere signatures.
2. Add authoritative quotes, availability enforcement and stable inventory/resource mapping.
3. Add automatic outbound queues, lifecycle consumers, retry and crash recovery.
4. Finish live payment/guarantee flows and verified settlement updates.
5. Replace Nexivo mock dashboards/statuses, fix generic sync and recovery/guest flows.
6. Configure real HTTPS URLs, matching secrets, tenant identities, connector records, policies and workers; align mobile/desktop release targets.
7. Run a test tenant through Nexivo → Central → each provider app → Central → Nexivo, asserting inventory, persisted bookings/orders, price, payment, cancellation, duplicate delivery, outage recovery and tenant isolation. Then validate deployed environments separately.

The existing Django/Next.js/Flutter applications do not need wholesale replacement based on this audit. The immediate work is to complete the missing bridges and replace placeholder data, status logic and payment behavior.
