import re
import socket
import subprocess

from django.conf import settings
from django.utils import timezone


def normalize_domain_host(host):
    value = (host or "").strip().lower()
    if not value:
        return ""
    return value.split(":")[0].rstrip(".")


def _parse_nslookup_txt(stdout):
    records = []
    for line in (stdout or "").splitlines():
        text = line.strip()
        if "text =" in text:
            _, _, raw = text.partition("text =")
            records.append(raw.strip().strip('"'))
    return records


def resolve_txt_records(host):
    host = normalize_domain_host(host)
    if not host:
        return {"ok": False, "records": [], "error": "missing_host", "method": "none"}

    try:
        import dns.resolver  # type: ignore

        answers = dns.resolver.resolve(host, "TXT")
        records = []
        for answer in answers:
            try:
                records.append("".join(part.decode("utf-8") for part in answer.strings))
            except Exception:
                records.append(str(answer).strip('"'))
        return {"ok": True, "records": records, "error": "", "method": "dnspython"}
    except Exception:
        pass

    if not bool(getattr(settings, "DOMAIN_VERIFICATION_ALLOW_NSLOOKUP", True)):
        return {
            "ok": False,
            "records": [],
            "error": "txt_lookup_unavailable",
            "method": "disabled",
        }

    try:
        cmd = ["nslookup", "-type=TXT", host]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=5)
        records = _parse_nslookup_txt(result.stdout)
        if records:
            return {"ok": True, "records": records, "error": "", "method": "nslookup"}
        return {
            "ok": False,
            "records": [],
            "error": "txt_record_not_found",
            "method": "nslookup",
        }
    except Exception:
        return {
            "ok": False,
            "records": [],
            "error": "txt_lookup_failed",
            "method": "nslookup",
        }


def resolve_host_addresses(host):
    host = normalize_domain_host(host)
    if not host:
        return {"ok": False, "addresses": [], "error": "missing_host"}
    try:
        infos = socket.getaddrinfo(host, None)
        addresses = sorted({row[4][0] for row in infos if row and row[4]})
        return {"ok": bool(addresses), "addresses": addresses, "error": ""}
    except socket.gaierror:
        return {"ok": False, "addresses": [], "error": "host_not_resolved"}


def verify_branding_custom_domain(branding):
    host = normalize_domain_host(branding.custom_domain)
    if not host:
        branding.domain_verification_status = "not_configured"
        branding.domain_failure_reason = "Custom domain is empty."
        branding.domain_last_checked_at = timezone.now()
        branding.save(
            update_fields=[
                "domain_verification_status",
                "domain_failure_reason",
                "domain_last_checked_at",
                "updated_at",
            ]
        )
        return {"verified": False, "reason": branding.domain_failure_reason, "host": host}

    if not branding.domain_verification_token:
        branding.domain_verification_status = "failed"
        branding.domain_failure_reason = "Missing domain verification token."
        branding.domain_last_checked_at = timezone.now()
        branding.save(
            update_fields=[
                "domain_verification_status",
                "domain_failure_reason",
                "domain_last_checked_at",
                "updated_at",
            ]
        )
        return {"verified": False, "reason": branding.domain_failure_reason, "host": host}

    address_check = resolve_host_addresses(host)
    if not address_check["ok"]:
        branding.domain_verification_status = "failed"
        branding.domain_failure_reason = "Domain has no resolvable A/AAAA record."
        branding.domain_last_checked_at = timezone.now()
        branding.save(
            update_fields=[
                "domain_verification_status",
                "domain_failure_reason",
                "domain_last_checked_at",
                "updated_at",
            ]
        )
        return {"verified": False, "reason": branding.domain_failure_reason, "host": host}

    txt_check = resolve_txt_records(host)
    expected = branding.domain_txt_record_value
    normalized_records = [re.sub(r"\s+", "", r.strip()) for r in txt_check.get("records", [])]
    matched = expected and re.sub(r"\s+", "", expected) in normalized_records
    if not matched:
        reason = "TXT verification record not found."
        if txt_check.get("error") == "txt_lookup_unavailable":
            reason = "TXT lookup unavailable on this server."
        branding.domain_verification_status = "failed"
        branding.domain_failure_reason = reason
        branding.domain_last_checked_at = timezone.now()
        branding.save(
            update_fields=[
                "domain_verification_status",
                "domain_failure_reason",
                "domain_last_checked_at",
                "updated_at",
            ]
        )
        return {"verified": False, "reason": reason, "host": host}

    branding.domain_verification_status = "verified"
    branding.domain_verified_at = timezone.now()
    branding.domain_last_checked_at = timezone.now()
    branding.domain_failure_reason = ""
    branding.save(
        update_fields=[
            "domain_verification_status",
            "domain_verified_at",
            "domain_last_checked_at",
            "domain_failure_reason",
            "updated_at",
        ]
    )
    return {"verified": True, "reason": "", "host": host}
