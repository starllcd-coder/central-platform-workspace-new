import base64
import hashlib
import hmac
import os
import secrets
import struct
import time


def generate_base32_secret():
    raw = base64.b32encode(os.urandom(20)).decode("ascii")
    return raw.rstrip("=")


def _normalize_secret(secret: str) -> bytes:
    value = (secret or "").strip().upper()
    padding = "=" * ((8 - (len(value) % 8)) % 8)
    return base64.b32decode(value + padding)


def _totp_for_counter(secret: str, counter: int, digits: int = 6) -> str:
    key = _normalize_secret(secret)
    msg = struct.pack(">Q", int(counter))
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    otp = code_int % (10**digits)
    return str(otp).zfill(digits)


def verify_totp(secret: str, code: str, *, step_seconds: int = 30, skew_steps: int = 1) -> bool:
    entered = "".join(ch for ch in str(code or "") if ch.isdigit())
    if len(entered) != 6:
        return False
    now_counter = int(time.time() // step_seconds)
    for delta in range(-abs(skew_steps), abs(skew_steps) + 1):
        if _totp_for_counter(secret, now_counter + delta) == entered:
            return True
    return False


def generate_backup_codes(count: int = 8):
    rows = []
    for _ in range(max(1, count)):
        code = f"{secrets.randbelow(10**4):04d}-{secrets.randbelow(10**4):04d}"
        rows.append(code)
    return rows


def normalize_backup_code(value: str) -> str:
    raw = str(value or "").strip().replace(" ", "")
    return raw.upper()


def backup_code_hash(code: str) -> str:
    normalized = normalize_backup_code(code)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
