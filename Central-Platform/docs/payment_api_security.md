# Payment API Request Signing

All `/payments/api/` requests require a timestamped HMAC signature. Gateway webhook routes use the provider webhook secret instead and do not use this internal-service scheme.

Required headers:

- `X-Payment-Timestamp`: current Unix timestamp in seconds.
- `X-Payment-Nonce`: a unique value no longer than 120 characters. It cannot be reused.
- `X-Payment-Signature`: lowercase SHA-256 HMAC hex digest.

Construct the signed bytes exactly as:

```text
timestamp + "." + nonce + "." + UPPERCASE_METHOD + "." + full_path_with_query + "." + raw_request_body
```

Sign those bytes with `PAYMENT_SERVICE_SECRET`. During rotation, Central Platform accepts both `PAYMENT_SERVICE_SECRET` and `PAYMENT_SERVICE_SECRET_NEXT`; callers should move to the next key before it becomes active.

Requests are rejected when the signature is invalid, the timestamp exceeds `PAYMENT_SIGNATURE_MAX_SKEW_SECONDS`, or the nonce has already been used. Keep clocks synchronized and generate a new nonce for every retry.

Production must set `PAYMENT_GATEWAY_MODE=disabled` until real gateway adapters and credentials are configured. Mock adapters cannot run in production.
