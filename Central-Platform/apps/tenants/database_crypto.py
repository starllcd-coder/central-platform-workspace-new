import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


PREFIX = "enc::"


def _fernet():
    source = settings.TENANT_DATABASE_ENCRYPTION_KEY.encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(source).digest())
    return Fernet(key)


def encrypt_database_secret(value):
    raw = str(value or "")
    if not raw:
        return ""
    if raw.startswith(PREFIX):
        return raw
    token = _fernet().encrypt(raw.encode("utf-8")).decode("ascii")
    return f"{PREFIX}{token}"


def decrypt_database_secret(value):
    stored = str(value or "")
    if not stored:
        return ""
    if not stored.startswith(PREFIX):
        return stored
    try:
        return _fernet().decrypt(stored[len(PREFIX) :].encode("ascii")).decode("utf-8")
    except InvalidToken:
        return ""
