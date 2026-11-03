import os


_env = os.getenv("DJANGO_ENV", "development").strip().lower()

if _env in {"prod", "production"}:
    from .production import *  # noqa: F401,F403
else:
    from .development import *  # noqa: F401,F403

