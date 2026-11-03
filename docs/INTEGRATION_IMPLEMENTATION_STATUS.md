# Integration implementation status — 3 November 2026

This is the current implementation record. Earlier audit and progress files describe earlier batches, including gaps addressed here. The applications are not deployed and domains have not been purchased. Local verification does not establish hosted or merchant readiness.

## Implemented locally

- DriveSphere, StayLux and Laundrex publish multiple inventory resources and prices through signed, retryable outboxes. Central scopes listings to enabled tenant/module bindings. Nexivo reads those listings with pagination.
- Quotes use native availability and pricing services, with date/quantity limits, currency checks and signed expiring review tokens. Confirmation rechecks current prices and terms. Booking receivers preserve native domain rules and reject duplicate or conflicting deliveries.
- Central dispatches bookings to the appropriate product and receives lifecycle updates. Verified payment and refund events are delivered into each product's native accounting records, with delivery receipts and retries.
- Nexivo customer recovery, booking confirmations, checkout review and account history use Central services. Partner and administrator dashboards read scoped records; unavailable metrics do not invent activity.
- Shared web sign-in uses explicit links to existing local accounts, short-lived one-use tickets and browser state binding. Local permissions remain authoritative. Optional Central credential fallback requires an existing account link.
- Stripe and Thawani hosted checkout adapters, authenticated payment verification, native webhook handling, refund tracking and reconciliation are implemented. Thawani supports full refunds only in this implementation. Merchant sandbox verification remains required, particularly for the Thawani API contract.
- Development checkout remains available in mock mode and reports zero money charged. Production mode never silently falls back to mock payments.
- Health/capability reporting, readiness checks, environment preparation and mobile release URL tooling are provided.

Existing themes and stylesheets were retained; new flows reuse existing components. Regression tests passed, but pixel-level equivalence and every desktop/mobile feature have not been certified.

## Verification

- Central: 92 tests passed, covering accounts, tenants, marketplace, connectors, payments, billing and stays.
- DriveSphere: 47 tests passed, including existing behavior and bridge/outbox coverage.
- StayLux: 69 tests passed, including native booking and offline synchronization coverage.
- Laundrex: 22 tests passed, including native order, access-control and integration coverage.
- Total: 230 backend tests passed. Migration drift checks passed for all four backends.
- Nexivo typecheck and production build passed.
- `python scripts/integration_probe.py` passed 35 checks across all five services using isolated temporary databases and generated fixture identities. It covers inventory, quotes, bookings, acknowledgements, simulated accounting/refunds, lifecycle propagation, customer cookie authentication and one-use sign-in. Latest evidence: `.runtime/probe-20261103-165146/result.json`; fixture configuration contains secrets and must remain private.
- No real gateway payment, application database migration or production deployment was performed.
- Flutter bootstrap was attempted, but the Dart SDK download failed due a network/TLS error. Flutter analysis, native builds, signing and device verification remain outstanding.

## Deployment sequence after domains and accounts are available

1. Assign HTTPS origins and real tenant, StayLux property and Laundrex branch identities in a private copy of `deployment/targets.example.json`. Supply independent Django signing keys and strong connector/Nexivo secrets through the environment. Run `python scripts/prepare-integration-env.py <targets.json>` to prepare separate private bundles. Add production databases, SMTP and gateway configuration; generated bundles are not a complete deployment configuration.
2. Back up each deployment database, apply each application's migrations through its normal release process, and configure Central's enabled tenant/module bindings and AppConnector records. Set connector `base_url` and browser-facing `public_url` to the intended product origin. Product and Central connector secrets must match.
3. Set explicit Central account links using each product's `python manage.py link_central_account <central-user-id> <local-user-id>`. This links existing accounts; it does not create users or grant local roles. Configure Central MFA for privileged access.
4. Run `python manage.py publish_central_inventory` in each product, then supervise `python manage.py flush_central_outbox --watch` as a separate worker. Configure Central's booking dispatch, payment-update dispatch and gateway reconciliation schedules. Inspect delivery failures rather than discarding them.
5. Configure Stripe/Thawani keys with Central's `configure_checkout_gateway` command, which reads environment secrets without printing them. Register gateway callbacks and webhook secrets using deployed HTTPS origins. Complete merchant sandbox checkout, cancellation, webhook replay, full refund and reconciliation tests before enabling real transactions. Thawani partial refunds are deliberately disabled.
6. Verify SMTP password-reset delivery, cookie security, privileged MFA and account permissions. Run Central `python manage.py integration_readiness --check-http --production`. A passing preflight is configuration evidence, not a substitute for real hosted booking and gateway tests.
7. Use `scripts/build-flutter-release.ps1` with actual product HTTPS origins and the required Flutter/Android tooling. Test native mobile and desktop clients against their product APIs, including existing offline workflows. iOS requires the appropriate Apple build/signing environment.
8. Complete a hosted end-to-end booking for all three products through Nexivo and confirm native accounting, lifecycle changes and refund results before launch.

Inventory updates are event based. Saves made while synchronization is disabled do not enqueue updates. Initial publication sends existing resources; it is not a destructive full catalog reconciliation. Review and deactivate stale Central listings when reconnecting a catalog after offline deletions.

Actual domains, hosting, merchant credentials, email transport and native signing/device environments remain external requirements. Until those checks pass, the accurate status is locally implemented and tested, with production verification pending.
