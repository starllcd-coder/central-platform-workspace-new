import os


def init_sentry_if_configured():
    dsn = str(os.getenv("SENTRY_DSN", "") or "").strip()
    if not dsn:
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=dsn,
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
            environment=os.getenv("SENTRY_ENVIRONMENT", os.getenv("DJANGO_ENV", "production")),
            send_default_pii=False,
        )
        return True
    except Exception:
        return False
