from __future__ import absolute_import, unicode_literals

try:
    from config.celery import app as celery_app
except Exception:  # pragma: no cover
    celery_app = None

__all__ = ("celery_app",)
