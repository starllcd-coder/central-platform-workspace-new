import os
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DJANGO_ENV = os.getenv("DJANGO_ENV", "development").strip().lower()
IS_PRODUCTION = DJANGO_ENV in {"production", "prod"}

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-this")
TENANT_DATABASE_ENCRYPTION_KEY = os.getenv(
    "TENANT_DATABASE_ENCRYPTION_KEY", SECRET_KEY
)
DEBUG = _as_bool(os.getenv("DJANGO_DEBUG"), default=False)
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
    "apps.accounts",
    "apps.connectors",
    "apps.ops",
    "apps.tenants",
    "apps.pricing",
    "apps.billing",
    "apps.paymentsvc",
    "apps.stay",
    "apps.marketplace",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "apps.connectors.middleware.ApiGovernanceMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.accounts.middleware.TenantContextMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if IS_PRODUCTION:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.accounts.context_processors.permission_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

db_backend = os.getenv("DJANGO_DB_BACKEND", "sqlite").strip().lower()
if db_backend in {"postgres", "postgresql", "psql"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DJANGO_DB_NAME", "central_platform"),
            "USER": os.getenv("DJANGO_DB_USER", "postgres"),
            "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", ""),
            "HOST": os.getenv("DJANGO_DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
            "CONN_MAX_AGE": int(os.getenv("DJANGO_DB_CONN_MAX_AGE", "60")),
            "OPTIONS": {
                "sslmode": os.getenv(
                    "DJANGO_DB_SSLMODE", "require" if IS_PRODUCTION else "prefer"
                ),
                "connect_timeout": int(os.getenv("DJANGO_DB_CONNECT_TIMEOUT", "10")),
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dubai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "assets"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if IS_PRODUCTION
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        )
    },
}

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
SSO_TOKEN_MAX_AGE = int(os.getenv("SSO_TOKEN_MAX_AGE", "3600"))
CONNECTOR_SHARED_SECRET = os.getenv("CONNECTOR_SHARED_SECRET", "dev-connector-secret")
MARKETPLACE_FINALIZE_SECRET = os.getenv("MARKETPLACE_FINALIZE_SECRET", "dev-marketplace-finalize-secret")
NEXIVO_LEAD_SHARED_SECRET = os.getenv("NEXIVO_LEAD_SHARED_SECRET", "dev-nexivo-lead-secret")
NEXIVO_LEAD_SIGNATURE_MAX_SKEW_SECONDS = int(
    os.getenv("NEXIVO_LEAD_SIGNATURE_MAX_SKEW_SECONDS", "300")
)
CONNECTOR_SHARED_SECRET_NEXT = os.getenv("CONNECTOR_SHARED_SECRET_NEXT", "")
CONNECTOR_REQUIRE_SIGNED_REQUESTS = _as_bool(
    os.getenv("CONNECTOR_REQUIRE_SIGNED_REQUESTS"), default=False
)
CONNECTOR_SIGNATURE_MAX_SKEW_SECONDS = int(
    os.getenv("CONNECTOR_SIGNATURE_MAX_SKEW_SECONDS", "300")
)
CONNECTOR_NONCE_RETENTION_DAYS = int(os.getenv("CONNECTOR_NONCE_RETENTION_DAYS", "7"))
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@central.local")
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = _as_bool(os.getenv("EMAIL_USE_TLS"), default=True)
NOTIFICATION_WEBHOOK_TIMEOUT = int(os.getenv("NOTIFICATION_WEBHOOK_TIMEOUT", "6"))
SMS_PROVIDER = os.getenv("SMS_PROVIDER", "mock")
OPS_WORKER_INTERVAL_SECONDS = int(os.getenv("OPS_WORKER_INTERVAL_SECONDS", "30"))
PRICING_SUBSCRIPTION_CUTOFF_DATE = date.fromisoformat(
    os.getenv("PRICING_SUBSCRIPTION_CUTOFF_DATE", "2026-01-01")
)
MARKETPLACE_FREE_DAYS = int(os.getenv("MARKETPLACE_FREE_DAYS", "60"))
API_VERSION = os.getenv("API_VERSION", "2026-04-19")
API_DEPRECATION_DATE = os.getenv("API_DEPRECATION_DATE", "")
API_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("API_RATE_LIMIT_WINDOW_SECONDS", "60"))
API_RATE_LIMIT_REQUESTS = int(os.getenv("API_RATE_LIMIT_REQUESTS", "120"))
API_RATE_LIMIT_CONNECTOR_REQUESTS = int(os.getenv("API_RATE_LIMIT_CONNECTOR_REQUESTS", "300"))
DOMAIN_VERIFICATION_ALLOW_NSLOOKUP = _as_bool(
    os.getenv("DOMAIN_VERIFICATION_ALLOW_NSLOOKUP"),
    default=True,
)

# Per-business database provisioning. The admin account must be allowed to
# create databases and restricted login roles/users on the target server.
TENANT_DB_CONNECT_TIMEOUT = int(os.getenv("TENANT_DB_CONNECT_TIMEOUT", "10"))
TENANT_DB_POSTGRES_HOST = os.getenv("TENANT_DB_POSTGRES_HOST", os.getenv("DJANGO_DB_HOST", "127.0.0.1"))
TENANT_DB_POSTGRES_PORT = int(os.getenv("TENANT_DB_POSTGRES_PORT", os.getenv("DJANGO_DB_PORT", "5432")))
TENANT_DB_POSTGRES_ADMIN_DATABASE = os.getenv("TENANT_DB_POSTGRES_ADMIN_DATABASE", "postgres")
TENANT_DB_POSTGRES_ADMIN_USER = os.getenv("TENANT_DB_POSTGRES_ADMIN_USER", os.getenv("DJANGO_DB_USER", "postgres"))
TENANT_DB_POSTGRES_ADMIN_PASSWORD = os.getenv("TENANT_DB_POSTGRES_ADMIN_PASSWORD", os.getenv("DJANGO_DB_PASSWORD", ""))
TENANT_DB_POSTGRES_SSLMODE = os.getenv("TENANT_DB_POSTGRES_SSLMODE", "prefer")
TENANT_DB_MYSQL_HOST = os.getenv("TENANT_DB_MYSQL_HOST", "127.0.0.1")
TENANT_DB_MYSQL_PORT = int(os.getenv("TENANT_DB_MYSQL_PORT", "3306"))
TENANT_DB_MYSQL_ADMIN_USER = os.getenv("TENANT_DB_MYSQL_ADMIN_USER", "root")
TENANT_DB_MYSQL_ADMIN_PASSWORD = os.getenv("TENANT_DB_MYSQL_ADMIN_PASSWORD", "")
TENANT_DB_MYSQL_SSLMODE = os.getenv("TENANT_DB_MYSQL_SSLMODE", "preferred")
TENANT_APP_PROVISIONER_URL = os.getenv("TENANT_APP_PROVISIONER_URL", "")
TENANT_APP_PROVISIONER_SECRET = os.getenv("TENANT_APP_PROVISIONER_SECRET", "")
TENANT_APP_PROVISIONER_TIMEOUT = int(os.getenv("TENANT_APP_PROVISIONER_TIMEOUT", "120"))

# Async worker configuration (Celery + Redis)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = _as_bool(os.getenv("CELERY_TASK_ALWAYS_EAGER"), default=False)
CELERY_TASK_EAGER_PROPAGATES = _as_bool(os.getenv("CELERY_TASK_EAGER_PROPAGATES"), default=True)
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "pricing-reconcile-subscriptions-every-hour": {
        "task": "apps.pricing.tasks.reconcile_subscriptions_task",
        "schedule": int(os.getenv("CELERY_RECONCILE_EVERY_SECONDS", "3600")),
        "args": (),
    },
    "ops-process-notifications-every-minute": {
        "task": "apps.ops.tasks.process_notifications_task",
        "schedule": int(os.getenv("CELERY_NOTIFICATIONS_EVERY_SECONDS", "60")),
        "args": (),
    },
    "ops-monitor-health-every-5-minutes": {
        "task": "apps.ops.tasks.monitor_platform_health_task",
        "schedule": int(os.getenv("CELERY_OPS_HEALTH_EVERY_SECONDS", "300")),
        "args": (),
    },
    "connectors-prune-nonces-daily": {
        "task": "apps.connectors.tasks.prune_connector_nonces_task",
        "schedule": int(os.getenv("CELERY_CONNECTORS_NONCE_PRUNE_EVERY_SECONDS", "86400")),
        "args": (),
    },
    "connectors-dispatch-marketplace-bookings": {
        "task": "apps.connectors.tasks.dispatch_marketplace_bookings_task",
        "schedule": int(os.getenv("CELERY_CONNECTOR_DISPATCH_EVERY_SECONDS", "30")),
        "args": (100,),
    },
    "payments-prune-request-nonces-daily": {
        "task": "apps.paymentsvc.tasks.prune_payment_nonces_task",
        "schedule": int(os.getenv("CELERY_PAYMENT_NONCE_PRUNE_EVERY_SECONDS", "86400")),
        "args": (),
    },
}
CONNECTOR_DISPATCH_MAX_ATTEMPTS = int(os.getenv("CONNECTOR_DISPATCH_MAX_ATTEMPTS", "8"))
OPS_ALERT_WINDOW_MINUTES = int(os.getenv("OPS_ALERT_WINDOW_MINUTES", "15"))
OPS_ALERT_MAX_FAILED_NOTIFICATIONS = int(os.getenv("OPS_ALERT_MAX_FAILED_NOTIFICATIONS", "10"))
OPS_ALERT_MAX_CONNECTOR_FAILURES = int(os.getenv("OPS_ALERT_MAX_CONNECTOR_FAILURES", "20"))
OPS_ALERT_EMAIL = os.getenv("OPS_ALERT_EMAIL", "")

TWO_FACTOR_ISSUER = os.getenv("TWO_FACTOR_ISSUER", "CentralPlatform")
TWO_FACTOR_PRIVILEGED_SESSION_SECONDS = int(
    os.getenv("TWO_FACTOR_PRIVILEGED_SESSION_SECONDS", "1800")
)
TWO_FACTOR_MANDATORY_FOR_SUPERUSER = _as_bool(
    os.getenv("TWO_FACTOR_MANDATORY_FOR_SUPERUSER"),
    default=True,
)
TWO_FACTOR_MANDATORY_PERMISSION_CODES = tuple(
    item.strip()
    for item in os.getenv(
        "TWO_FACTOR_MANDATORY_PERMISSION_CODES",
        "billing.manage,commission.manage",
    ).split(",")
    if item.strip()
)
TWO_FACTOR_PROTECTED_PERMISSION_PREFIXES = tuple(
    item.strip()
    for item in os.getenv(
        "TWO_FACTOR_PROTECTED_PERMISSION_PREFIXES",
        "billing.,commission.,ops.,pricing.",
    ).split(",")
    if item.strip()
)
REAUTH_PROTECTED_PERMISSION_PREFIXES = tuple(
    item.strip()
    for item in os.getenv(
        "REAUTH_PROTECTED_PERMISSION_PREFIXES",
        "billing.,commission.",
    ).split(",")
    if item.strip()
)
REAUTH_SESSION_SECONDS = int(os.getenv("REAUTH_SESSION_SECONDS", "900"))

PAYMENT_SERVICE_SECRET = os.getenv("PAYMENT_SERVICE_SECRET", "dev-payment-service-secret")
PAYMENT_SERVICE_SECRET_NEXT = os.getenv("PAYMENT_SERVICE_SECRET_NEXT", "")
PAYMENT_SIGNATURE_MAX_SKEW_SECONDS = int(
    os.getenv("PAYMENT_SIGNATURE_MAX_SKEW_SECONDS", "300")
)
PAYMENT_NONCE_RETENTION_DAYS = int(os.getenv("PAYMENT_NONCE_RETENTION_DAYS", "7"))
PAYMENT_GATEWAY_MODE = os.getenv(
    "PAYMENT_GATEWAY_MODE", "disabled" if IS_PRODUCTION else "mock"
).strip().lower()

cache_url = os.getenv(
    "DJANGO_CACHE_URL",
    "redis://127.0.0.1:6379/1" if IS_PRODUCTION else "",
).strip()
if cache_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": cache_url,
            "KEY_PREFIX": os.getenv("DJANGO_CACHE_KEY_PREFIX", "central-platform"),
        }
    }

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = _as_bool(os.getenv("DJANGO_SESSION_COOKIE_SECURE"), default=False)
CSRF_COOKIE_SECURE = _as_bool(os.getenv("DJANGO_CSRF_COOKIE_SECURE"), default=False)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if IS_PRODUCTION:
    if SECRET_KEY in {"", "dev-only-change-this", "change-me"}:
        raise RuntimeError("DJANGO_SECRET_KEY must be set to a strong value in production.")
    if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 12:
        raise RuntimeError("DJANGO_SECRET_KEY must be at least 50 characters with sufficient entropy.")
    if not any(h.strip() and h.strip() not in {"127.0.0.1", "localhost"} for h in ALLOWED_HOSTS):
        raise RuntimeError("DJANGO_ALLOWED_HOSTS must include production hostnames.")
    if db_backend not in {"postgres", "postgresql", "psql"}:
        raise RuntimeError("Production requires PostgreSQL; set DJANGO_DB_BACKEND=postgres.")
    if CONNECTOR_SHARED_SECRET in {"", "dev-connector-secret"}:
        raise RuntimeError("CONNECTOR_SHARED_SECRET must be set to a strong value in production.")
    if MARKETPLACE_FINALIZE_SECRET in {"", "dev-marketplace-finalize-secret"}:
        raise RuntimeError("MARKETPLACE_FINALIZE_SECRET must be set to a strong value in production.")
    if NEXIVO_LEAD_SHARED_SECRET in {"", "dev-nexivo-lead-secret"}:
        raise RuntimeError("NEXIVO_LEAD_SHARED_SECRET must be set to a strong value in production.")
    if TENANT_DATABASE_ENCRYPTION_KEY in {"", SECRET_KEY}:
        raise RuntimeError("TENANT_DATABASE_ENCRYPTION_KEY must be independently set in production.")
    if TENANT_APP_PROVISIONER_URL and not TENANT_APP_PROVISIONER_SECRET:
        raise RuntimeError("TENANT_APP_PROVISIONER_SECRET is required when TENANT_APP_PROVISIONER_URL is set.")
    if CONNECTOR_REQUIRE_SIGNED_REQUESTS and not CONNECTOR_SHARED_SECRET:
        raise RuntimeError("CONNECTOR_REQUIRE_SIGNED_REQUESTS=1 requires CONNECTOR_SHARED_SECRET.")
    if PAYMENT_SERVICE_SECRET in {"", "dev-payment-service-secret"}:
        raise RuntimeError("PAYMENT_SERVICE_SECRET must be set to a strong value in production.")
    if PAYMENT_GATEWAY_MODE not in {"disabled", "live"}:
        raise RuntimeError("PAYMENT_GATEWAY_MODE must be 'disabled' or 'live' in production.")
    if not cache_url or urlsplit(cache_url).password is None:
        raise RuntimeError("DJANGO_CACHE_URL must use authenticated Redis in production.")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structured",
        }
    },
    "root": {"handlers": ["console"], "level": os.getenv("DJANGO_LOG_LEVEL", "INFO")},
}

# Trusted destination for customer password recovery emails.
NEXIVO_PUBLIC_URL = os.getenv("NEXIVO_PUBLIC_URL", "http://localhost:3000")

MARKETPLACE_REQUIRE_QUOTES = _as_bool(os.getenv("MARKETPLACE_REQUIRE_QUOTES"), default=IS_PRODUCTION)

CELERY_BEAT_SCHEDULE["reconcile-gateway-payments"] = {"task": "apps.paymentsvc.tasks.reconcile_gateway_payments_task", "schedule": 60}

CELERY_BEAT_SCHEDULE["dispatch-payment-updates"] = {"task": "apps.connectors.tasks.dispatch_payment_updates_task", "schedule": 30}
