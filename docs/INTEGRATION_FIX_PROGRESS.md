# Current implementation record

See [INTEGRATION_IMPLEMENTATION_STATUS.md](INTEGRATION_IMPLEMENTATION_STATUS.md) for the latest implementation, verification and remaining deployment requirements. The entries below are historical batch records.

# Integration fixes — 3 November 2026

This records the first implementation batch following the audit. The systems are not yet ready for a production end-to-end sign-off.

## Implemented locally

- DriveSphere and StayLux now expose signed `POST /api/central/bookings/` receivers. Each verifies the configured tenant/module, signature timestamp, and database-backed nonce; persists a delivery receipt; rejects conflicting reuse of a booking ID; and acknowledges only persisted bookings.
- Both receivers use transactions, lock the requested resource and check availability. They reject a price or currency that differs from the provider's current base rate. DriveSphere calls its existing booking service; StayLux validates and freezes the booking price. Advanced seasonal pricing, taxes and discounts still need a shared quote contract.
- DriveSphere outbound signatures now include Central's required nonce. StayLux has a signed outbound client and `push_central_connector --kind tenant` diagnostic command.
- Central calculates booking base totals from listing price times duration/quantity, ignoring browser totals.
- Central dispatches use a five-minute claim lease, allowing interrupted dispatches to be retried.
- Nexivo stay/car estimates follow the selected dates. Booking routes no longer invent successful bookings after an upstream failure and preserve Central errors.
- Health/listing checks no longer label unrelated capabilities connected; mock connectors no longer count as launch ready. The unsupported generic sync route explicitly returns 501 instead of posting sync requests into sales leads.
- Connectivity preflight resolves workspace paths, validates JSON responses, sends signed tenant syncs only when requested with explicit tenant codes, and restores environment variables afterward.
- Gateway preference is **Thawani and Stripe**, replacing the earlier Tap selection. Payments default to disabled. Public checkout returns an unavailable response instead of a fake session. Online booking is rejected pending a real checkout implementation, and Nexivo disables online selection and removes placeholder card inputs.

## Validation

- Central connector, marketplace and payment suites: **37 tests passed**.
- DriveSphere bridge: **6 tests passed**; migration drift check passed.
- StayLux bridge: **6 tests passed** using the bridge URL configuration and no middleware; migration drift check passed. Full application checks remain limited by missing installed `openpyxl` and `whitenoise` dependencies.
- PowerShell preflight syntax parsed successfully. Network preflight was not run against a deployed environment.
- Nexivo changes were inspected but not built/typechecked: Node/npm are unavailable on PATH.

## Setup before enabling receivers

1. Install each application's declared dependencies.
2. In DriveSphere and StayLux run `python manage.py migrate` to create the bridge receipt and nonce tables. These migrations have been tested on temporary test databases; they have not been applied to application databases by this change.
3. Configure `CENTRAL_PLATFORM_URL`, `CENTRAL_CONNECTOR_SECRET`, `CENTRAL_CONNECTOR_SIGNED=1`, and `CENTRAL_TENANT_CODE`. The connector secret must match Central's `CONNECTOR_SHARED_SECRET`. StayLux also requires `CENTRAL_PROPERTY_ID`, explicitly binding the Central tenant to its local property.
4. Create/verify tenant-specific Central `AppConnector` records with the provider base URL. The dispatcher appends `/api/central/bookings/` automatically. Run Central's worker and scheduler.
5. Verify listing resource IDs and prices against the provider resource. Numeric resource IDs are interpreted as local primary keys; nonnumeric IDs use unit code/vehicle plate. Do not assume identical IDs in separate databases.
6. Run a controlled tenant test through Nexivo, Central and the actual receiver. Verify persisted provider records and retries. No deployment or live booking test has been performed yet.

## Work still required

- Automatic inventory/rate/availability publication and booking/order lifecycle updates for all three products, including cancellation and payment synchronization.
- Shared quotes covering provider pricing rules, taxes, currency precision, and policies; full concurrency tests against production PostgreSQL and all existing booking writers.
- Thawani and Stripe hosted checkout adapters, verified native webhooks, booking/payment linkage, card guarantees, refunds and reconciliation. Existing adapters are mocks and must not be enabled as live providers. A merchant account, appropriate approval and API credentials will be needed for real processing; do not paste secret keys into chat.
- Authenticated live partner/admin dashboards, password recovery, account linking/SSO, guest confirmation and remaining customer features.
- Integration status UI still has static capability data; complete per-capability probes rather than treating basic HTTP health as end-to-end proof.
- Full frontend/mobile builds, release API configuration, deployment setup and complete end-to-end tests.
- Provider nonce retention/pruning and long-term receipt management.

The original audit remains a record of findings at scan time; this file tracks which have since changed.

## Checkout update

Customer online checkout selection is restored. Development defaults to mock payment mode and persists online test bookings as `test_unpaid`; test payment sessions explicitly state that no money was collected. Production still defaults to disabled and disallows mock mode. Thawani and Stripe live adapters and merchant setup remain required before live checkout can process payments. Marketplace/payment regression suites: 26 tests passed after this update.


## Second implementation batch ? preservation and regression checks

Implemented:

- Added a `central_sync` app in DriveSphere, StayLux and Laundrex. Status saves for existing Central-origin bookings/orders enqueue signed status snapshots; saves make no network calls. The queue participates in the caller's transaction when one exists. This does not publish inventory or independent local bookings.
- Synchronization is off by default (`CENTRAL_SYNC_ENABLED=0`). Existing operations do not query the new tables while disabled. After migrations and configuration, `flush_central_outbox --watch` delivers events in a separate process with leases, backoff, stable event IDs, and retained dead events.
- Central applies lifecycle updates only to a matching tenant/module/booking, rejects invalid timestamps/statuses, ignores stale messages, and prevents terminal bookings from reopening. Payment state is not inferred from an operational status update. The dispatcher no longer sends cancelled/completed bookings or overwrites terminal status when acknowledgements race callbacks.
- Added `central_outbox_status`, `retry_central_event <uuid>`, and `prune_central_sync --dry-run` commands. Pruning preserves pending/dead events and booking delivery receipts; expired signed request nonces can be removed safely.
- Wired Nexivo password recovery through its existing form and added a reset page using existing auth components. Reset requests return the same response for eligible/unknown/inactive accounts, throttle by email, and use single-use expiring Django tokens. Resetting a password invalidates only that customer's old API tokens; existing tokens remain compatible until a reset occurs.
- Added signed read-only guest booking confirmation links, valid for 24 hours. Customer contact details are excluded. Existing booking forms now navigate to the confirmation page instead of sending guests straight into a protected account page. Network errors restore a usable form state. Development checkout remains available and explicitly reports no money collected.
- Corrected encoding damage found by the new frontend build check. No stylesheets, theme settings or existing dashboard layouts were changed. New pages reuse existing components. Visual pixel equivalence and all mobile/desktop runtimes have not been certified.
- Installed verification tools/dependencies under ignored `.tooling/` only. Node and npm are now available there; Nexivo dependencies were installed from its unchanged lockfile. No global runtime replacement was performed.

Validation for this batch:

- Central connector, marketplace, password recovery and payments: **52 tests passed**.
- DriveSphere existing regression suite: **29 tests passed**; bridge/outbox suite: **13 tests passed** before the final non-status-save filter, followed by a final verification run recorded below.
- Laundrex existing order/RBAC tests plus connector/outbox tests: **19 tests passed** before that filter, followed by a final verification run recorded below.
- StayLux full framework check passed after installing its missing declared export/static middleware dependencies. Its broader 62-test run exposed one existing test that expected an `on_commit` callback to run in a rollback-only `TestCase`. The test now explicitly executes commit callbacks. That exposed a separate real serializer failure; its correction and final rerun are recorded below.
- Nexivo typecheck passed and the latest production build passed, including 96 prerendered pages and the new dynamic recovery/confirmation routes. This is a build validation, not a live gateway or browser interaction test.
- Migration drift checks passed for the new apps and Central. Migrations remain unapplied to application databases; tests used temporary databases.

Enablement after review:

1. Apply Central marketplace migrations and the product `central_bridge` / `central_sync` migrations using each app's normal release process.
2. Configure matching connector secrets, tenant identities, HTTPS URLs, signing and StayLux's explicit property binding as described above. Then enable `CENTRAL_SYNC_ENABLED=1` per product.
3. Run `python manage.py flush_central_outbox --watch` under the deployment's process manager for each product, independently of its web process. Use `central_outbox_status` to inspect delivery health, retry only inspected dead events, and schedule nonce/delivered-event pruning.
4. Configure Central `NEXIVO_PUBLIC_URL` to the deployed Nexivo HTTPS origin and set its existing SMTP settings. Local console/locmem email validation does not prove actual email delivery.
5. Existing mobile/desktop clients were not redirected to Central; they retain their product API contracts.

Still outstanding: automatic inventory/rate/availability publication and the multi-resource listing model, full pricing/tax/policy contracts, live Thawani/Stripe adapters and merchant credentials, live partner/admin dashboards, shared sign-in/account linking, mobile/desktop runtime verification, process deployment and actual cross-service end-to-end sign-off. The local fixes do not mean these are complete.


### Additional StayLux sync correction

Executing the existing post-commit test exposed a real pre-existing failure: `model_to_dict` included file objects and decimal values that the JSON field could not encode. Sync writes silently failed, and a failed insert could leave an enclosing transaction unusable. The serializer now emits file paths, related IDs and JSON-safe price/date values; sync inserts use a savepoint and log failures. Six focused sync tests passed, including price/file serialization and transaction isolation. This fixes synchronization without changing existing booking prices or UI fields.


### Final verification results for this batch

- Central: **52 passed**.
- DriveSphere: **29 existing regression tests + 13 bridge/outbox tests passed**.
- StayLux: **64 passed** with its normal application URL configuration and installed local dependencies, including original core/booking/sync tests and new bridge/outbox tests.
- Laundrex: **19 passed**, covering existing order/RBAC tests and connector/outbox behavior.
- Total across these suites: **177 passed**. Nexivo production build and typecheck passed. Migration drift checks passed.
- No production deployment, payment charge, worker activation, application database migration, mobile build, or pixel-level visual certification was performed. Existing stylesheets/themes remain unchanged, and development checkout remains enabled.
