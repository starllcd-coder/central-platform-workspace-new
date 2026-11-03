# UAT Test Plan (StayLux, DriveSphere, Laundrex)

This plan validates end-to-end business flows before production go-live.

## Scope
- Tenant onboarding and access control
- Pricing and commission behavior
- Booking/payment/refund/dispute operations
- Notification and analytics visibility
- Agreement and policy enforcement

## Test Data Setup
1. Create 3 tenants:
   - `StayLux Demo`
   - `DriveSphere Demo`
   - `Laundrex Demo`
2. Assign module access per tenant.
3. Seed at least two users per tenant:
   - operations role
   - finance role
4. Ensure one super admin user is available.

## UAT Execution Rules
- Record each case as `PASS` or `FAIL`.
- On fail, capture:
  - steps
  - expected result
  - actual result
  - screenshot
  - blocker severity (`P0/P1/P2`)
- Re-test all failed cases after fixes.

## Core UAT Cases
1. Login and tenant switch
   - Login as super admin and tenant user.
   - Switch tenant from top bar.
   - Verify data scoping changes correctly.

2. RBAC enforcement
   - Attempt billing actions with read-only account.
   - Verify blocked actions return permission error.

3. Agreement compliance
   - Keep required agreements unaccepted.
   - Attempt billing transaction and booking webhook event.
   - Confirm operation is blocked.
   - Accept agreements and verify operation succeeds.

4. Pricing and commission
   - Create and activate commission rules.
   - Post booking payments with online and cash channels.
   - Verify commission/net amounts and settlement states.

5. Online payment flow
   - Post paid transaction (online).
   - Verify ledger entries, notifications, and billing list presence.

6. Cash on arrival flow
   - Post paid transaction (cash).
   - Verify commission receivable and cash invoice workflow.

7. Refund flow
   - Process full and partial refunds.
   - Verify transaction/refund records and recalculated financial fields.

8. Dispute flow
   - Create dispute.
   - Move through `open -> under_review -> resolved/rejected`.
   - Verify audit trail and notification generation.

9. Dispute triage UX
   - Use status chips and priority filters.
   - Validate urgency badges:
     - `Normal` (<24h)
     - `Attention` (24h-48h)
     - `High` (>48h)
   - Validate pending default sort behavior (oldest first when no manual sort).

10. Analytics and export
   - Load analytics with date and tenant filters.
   - Export analytics CSV and disputes CSV with filters.
   - Verify exported rows match filtered UI state.

11. Notifications worker
   - Queue notification events.
   - Run notification processor/worker.
   - Confirm retry behavior and final status updates.

12. Dashboard operations visibility
   - Verify dispute status cards and high-priority pending count.
   - Validate deep links open correct filtered dispute views.

## UAT Sign-off
Sign-off requires:
- No open `P0` or `P1` defects.
- All critical business flows passed for all 3 modules.
- Finance and ops owners approval.
