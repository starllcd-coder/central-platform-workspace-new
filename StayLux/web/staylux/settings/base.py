from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.environ.get("STAYLUX_APPDATA", BASE_DIR))

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",

    # Local apps
    "api",
    "core",
    "settings_app",
    "accounts",
    "inventory",
    "guests",
    "bookings.apps.BookingsConfig",
    "pricing",
    "contracts",
    "inspections",
    "billing",
    "housekeeping",
    "maintenance.apps.MaintenanceConfig",
    "owner_portal",
    "notifications",
    "audit",
    "reports",
    "mobile_api",
    "sync_engine",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "staylux.middleware.SimpleCORSMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "staylux.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.notification_badge",
            ],
        },
    },
]

WSGI_APPLICATION = "staylux.wsgi.application"

# Internationalization
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("ar", "Arabic")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static / media
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = DATA_DIR / "collected_static"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = DATA_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

# Auth redirects (UI)
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# Disabled until a Firebase project and server credentials are configured.
FIREBASE_PUSH_ENABLED = os.environ.get("FIREBASE_PUSH_ENABLED", "0") == "1"
FIREBASE_SERVICE_ACCOUNT_FILE = os.environ.get("FIREBASE_SERVICE_ACCOUNT_FILE", "")
CHANNEL_CREDENTIALS_KEY = os.environ.get("CHANNEL_CREDENTIALS_KEY", "")

# Signed Central marketplace booking bridge.
INSTALLED_APPS += ["central_bridge"]
CENTRAL_PLATFORM_URL = os.environ.get("CENTRAL_PLATFORM_URL", "http://127.0.0.1:8000")
CENTRAL_CONNECTOR_SECRET = os.environ.get("CENTRAL_CONNECTOR_SECRET", "")
CENTRAL_CONNECTOR_SIGNED = os.environ.get("CENTRAL_CONNECTOR_SIGNED", "1") == "1"
CENTRAL_TENANT_CODE = os.environ.get("CENTRAL_TENANT_CODE", "")
CENTRAL_MODULE_CODE = "staylux"
CENTRAL_PROPERTY_ID = os.environ.get("CENTRAL_PROPERTY_ID", "")

# Opt-in transactional Central status outbox. Migrate before enabling.
INSTALLED_APPS += ["central_sync"]
CENTRAL_SYNC_ENABLED = __import__("os").environ.get("CENTRAL_SYNC_ENABLED", "0") == "1"

CENTRAL_SSO_ENABLED = __import__("os").environ.get("CENTRAL_SSO_ENABLED", "0") == "1"

CENTRAL_NEXIVO_URL = __import__("os").environ.get("CENTRAL_NEXIVO_URL", "http://localhost:3000")

if CENTRAL_SSO_ENABLED:
    AUTHENTICATION_BACKENDS = list(globals().get("AUTHENTICATION_BACKENDS", ["django.contrib.auth.backends.ModelBackend"])) + ["central_sync.auth_backend.MappedCentralBackend"]
