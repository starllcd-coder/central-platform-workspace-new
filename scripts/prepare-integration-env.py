"""Generate isolated environment bundles from reviewed deployment targets, without printing secrets."""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def origin(value, local):
    value = str(value).rstrip("/")
    parsed = urlsplit(value)
    if not parsed.hostname or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("Use a base origin without credentials, paths, query or fragment.")
    if parsed.hostname.endswith(".invalid") or (not local and (parsed.scheme != "https" or parsed.hostname in {"localhost", "127.0.0.1"})):
        raise ValueError("Replace example domains with real HTTPS origins before production deployment.")
    if local and parsed.scheme not in {"http", "https"}:
        raise ValueError("Local origins must use HTTP or HTTPS.")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / ".runtime/release-env")
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.config.read_text(encoding="utf-8"))
    central, nexivo = origin(data["centralUrl"], args.local), origin(data["nexivoUrl"], args.local)
    secret = os.getenv("CONNECTOR_SHARED_SECRET", "")
    if len(secret) < 32:
        raise ValueError("Set CONNECTOR_SHARED_SECRET to a value of at least 32 characters before generating bundles.")
    bundles = {"Central-Platform": {"DJANGO_ENV": "development" if args.local else "production", "CONNECTOR_SHARED_SECRET": secret,
        "CONNECTOR_REQUIRE_SIGNED_REQUESTS": "1", "NEXIVO_PUBLIC_URL": nexivo, "MARKETPLACE_REQUIRE_QUOTES": "1",
        "PAYMENT_GATEWAY_MODE": "mock" if args.local else "live"},
        "nexivo": {"CENTRAL_PLATFORM_API_URL": central + "/api", "NEXT_PUBLIC_CENTRAL_PLATFORM_API": central + "/api", "NEXIVO_ALLOW_MOCK_FALLBACK": "0"}}
    for key, env_name in [("NEXIVO_SESSION_SECRET", "NEXIVO_SESSION_SECRET"), ("NEXIVO_LEAD_SHARED_SECRET", "NEXIVO_LEAD_SHARED_SECRET")]:
        value = os.getenv(env_name, "")
        if len(value) < 32:
            raise ValueError(f"Set {env_name} to a strong value before generating bundles.")
        bundles["nexivo"][key] = value
        if key == "NEXIVO_LEAD_SHARED_SECRET":
            bundles["Central-Platform"][key] = value
    for module, directory in [("drivesphere", "DriveSphere"), ("staylux", "StayLux"), ("laundrex", "Laundrex")]:
        product = data["products"][module]
        base = origin(product["baseUrl"], args.local)
        tenant = str(product["tenantCode"])
        if not tenant or tenant.startswith("SET-"):
            raise ValueError("Use actual Central tenant codes.")
        bundles[directory] = {"DJANGO_ENV": "development" if args.local else "production", "CENTRAL_PLATFORM_URL": central,
            "CENTRAL_NEXIVO_URL": nexivo, "CENTRAL_CONNECTOR_SECRET": secret, "CENTRAL_CONNECTOR_SIGNED": "1",
            "CENTRAL_TENANT_CODE": tenant, "CENTRAL_MODULE_CODE": module, "CENTRAL_SYNC_ENABLED": "1", "CENTRAL_SSO_ENABLED": "1",
            "DJANGO_ALLOWED_HOSTS": urlsplit(base).hostname}
        if module == "staylux":
            prop = str(product.get("propertyId", ""))
            if not prop.isdigit():
                raise ValueError("Set StayLux's actual local property ID.")
            bundles[directory]["CENTRAL_PROPERTY_ID"] = prop
        if module == "laundrex":
            branch = str(product.get("branchCode", ""))
            if not branch or branch.startswith("SET-"):
                raise ValueError("Set Laundrex's actual local branch code.")
            bundles[directory]["CENTRAL_BRANCH_CODE"] = branch
            bundles[directory]["CENTRAL_CURRENCY"] = product.get("currency", "OMR")
    bundles["Central-Platform"]["DJANGO_ALLOWED_HOSTS"] = urlsplit(central).hostname
    for app, variables in bundles.items():
        if app != "nexivo":
            key_name = app.upper().replace("-", "_") + "_DJANGO_SECRET_KEY"
            key = os.getenv(key_name, "")
            if len(key) < 32:
                raise ValueError(f"Set {key_name}; each app must use its own Django signing key.")
            variables["DJANGO_SECRET_KEY"] = key
        if any("\n" in str(value) or "\r" in str(value) for value in variables.values()):
            raise ValueError("Environment values must not contain newlines.")
    args.output.mkdir(parents=True, exist_ok=True)
    for app, variables in bundles.items():
        target = args.output / (app + ".env")
        if target.exists():
            raise ValueError(f"Refusing to overwrite {target}; review existing deployment configuration first.")
    for app, variables in bundles.items():
        target = args.output / (app + ".env")
        target.write_text("# Generated after validating the target origins. Add database, SMTP and gateway settings separately.\n" +
            "\n".join(f"{key}={json.dumps(str(value))}" for key, value in variables.items()) + "\n", encoding="utf-8")
        print("Prepared", target)
    print("No application database, user account, gateway mode or hosted service was changed. Review and load each bundle in its own service environment.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as exc:
        raise SystemExit(str(exc))
