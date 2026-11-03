from .base import *  # noqa: F401,F403
from .base import _as_bool

from config.observability import init_sentry_if_configured
from django.core.exceptions import ImproperlyConfigured

DEBUG = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CONNECTOR_REQUIRE_SIGNED_REQUESTS = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = _as_bool(  # noqa: F405
    os.getenv("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS"), default=True
)
SECURE_HSTS_PRELOAD = _as_bool(os.getenv("DJANGO_SECURE_HSTS_PRELOAD"), default=True)  # noqa: F405
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

if SMS_PROVIDER.strip().lower() == "mock":  # noqa: F405
    raise ImproperlyConfigured("SMS_PROVIDER must use a real provider in production.")
if EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":  # noqa: F405
    raise ImproperlyConfigured("EMAIL_BACKEND must use a real provider in production.")
if not EMAIL_HOST:  # noqa: F405
    raise ImproperlyConfigured("EMAIL_HOST must be configured in production.")
if DEFAULT_FROM_EMAIL.endswith(".local"):  # noqa: F405
    raise ImproperlyConfigured("DEFAULT_FROM_EMAIL must use a deliverable production domain.")

init_sentry_if_configured()
