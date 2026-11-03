# Integration Contract v1

## Connector Auth
- Header required for machine-to-machine calls:
  - `X-Connector-Secret: <CONNECTOR_SHARED_SECRET>`

## SSO Flow
1. Central platform issues token:
   - `POST /accounts/api/sso/token/`
2. App backend validates token:
   - `POST /accounts/api/sso/introspect/`

### Token issue payload
```json
{
  "user_id": 1,
  "tenant_id": 1,
  "module_codes": ["drivesphere"]
}
```

## Connector Endpoints
- `GET /api/connectors/health/`
- `POST /api/connectors/tenant/sync/`
- `POST /api/connectors/usage/report/`
- `POST /api/connectors/webhooks/events/`

## Billing Write Endpoint
- `POST /billing/api/transactions/`
- `POST /billing/api/transactions/<id>/refund/`

### Billing transaction payload
```json
{
  "tenant": 1,
  "module": 2,
  "booking_ref": "BKG-1002",
  "payment_channel": "online",
  "booking_type": "online",
  "gross_amount": "180.00",
  "gateway_fee": "4.20",
  "tax_amount": "0.00",
  "currency": "OMR",
  "occurred_at": "2026-04-17T18:10",
  "metadata": {
    "source_app": "drivesphere"
  }
}
```

### Refund payload
```json
{
  "refund_type": "partial",
  "refund_percent": "50.00",
  "reason": "Customer cancelled within policy window"
}
```

## Tenant Sync Payload
```json
{
  "tenant_code": "TNT-001",
  "module_code": "drivesphere",
  "status": "active"
}
```

## Usage Report Payload
```json
{
  "tenant_code": "TNT-001",
  "module_code": "drivesphere",
  "period": "2026-04",
  "bookings_count": 120,
  "gross_amount": 8320.50
}
```

## Webhook Event Payload
```json
{
  "tenant_code": "TNT-001",
  "module_code": "staylux",
  "event_name": "booking.created",
  "event_id": "evt_123",
  "data": {
    "booking_id": "BKG-1"
  }
}
```

## Agreement Enforcement
- Marketplace booking events (`event_name` starts with `booking.`) require accepted agreements:
  - `TOS`
  - `COMMISSION`
  - `PAYMENT`
- If missing, connector webhook returns `409` with:
```json
{
  "accepted": false,
  "detail": "Required marketplace agreements are missing.",
  "missing_agreements": ["COMMISSION"]
}
```
