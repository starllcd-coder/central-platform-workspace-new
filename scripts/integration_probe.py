"""Isolated local integration probe. Never uses application or production databases."""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, build_opener, HTTPCookieProcessor, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[1]
APPS = {
    "central": ("Central-Platform", "config.settings.development"),
    "drivesphere": ("DriveSphere/web", "config.settings.dev"),
    "staylux": ("StayLux/web", "staylux.settings.development"),
    "laundrex": ("Laundrex", "laundrex.settings"),
}
OWNER = "integration-owner@example.test"
CUSTOMER = "integration-customer@example.test"


def configure(app, runtime):
    config = json.loads((runtime / "config.json").read_text(encoding="utf-8"))
    folder, module = APPS[app]
    sys.path.insert(0, str(ROOT / folder))
    sys.path.insert(0, str(ROOT / ".tooling/python"))
    os.environ["DJANGO_SETTINGS_MODULE"] = module
    os.environ["DJANGO_ENV"] = "development"
    from django.conf import settings

    # Override before app initialization. Existing DB files are never opened.
    settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": str(runtime / f"{app}.sqlite3"), "OPTIONS": {"timeout": 30}}}
    settings.SECRET_KEY = config["secret"] + app
    settings.DEBUG = True
    settings.ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
    settings.SECURE_SSL_REDIRECT = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_SECURE = False
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.CONNECTOR_SHARED_SECRET = config["secret"]
    settings.CONNECTOR_REQUIRE_SIGNED_REQUESTS = True
    settings.PAYMENT_GATEWAY_MODE = "mock"
    settings.MARKETPLACE_REQUIRE_QUOTES = True
    settings.NEXIVO_PUBLIC_URL = config["urls"]["nexivo"]
    settings.CENTRAL_PLATFORM_URL = config["urls"]["central"]
    settings.CENTRAL_NEXIVO_URL = config["urls"]["nexivo"]
    settings.CENTRAL_CONNECTOR_SECRET = config["secret"]
    settings.CENTRAL_CONNECTOR_SIGNED = True
    settings.CENTRAL_SYNC_ENABLED = True
    settings.CENTRAL_SSO_ENABLED = True
    settings.CENTRAL_MODULE_CODE = app
    settings.CENTRAL_TENANT_CODE = "PROBE-" + app.upper()
    settings.CENTRAL_PROPERTY_ID = 1
    settings.CENTRAL_BRANCH_CODE = "muscat"
    settings.CENTRAL_CURRENCY = "OMR"
    settings.API_RATE_LIMIT_REQUESTS = 10000
    settings.API_RATE_LIMIT_CONNECTOR_REQUESTS = 10000
    import django
    django.setup()
    return config


def seed(app, config):
    from django.core.management import call_command
    from django.contrib.auth import get_user_model
    call_command("migrate", interactive=False, verbosity=0)
    User = get_user_model()
    user = User.objects.create_superuser(username="integration-owner", email=OWNER, password=config["password"])
    if app == "central":
        from apps.accounts.models import TenantMembership, Role, MembershipRole
        from apps.connectors.models import AppConnector
        from apps.tenants.models import Tenant, Module, TenantModule
        role, _ = Role.objects.get_or_create(code="tenant.owner", defaults={"name": "Owner"})
        for code in ("drivesphere", "staylux", "laundrex"):
            tenant = Tenant.objects.create(tenant_code="PROBE-" + code.upper(), name="Integration " + code, status="active", currency="OMR", account_type="production")
            module, _ = Module.objects.get_or_create(code=code, defaults={"name": code.title()})
            TenantModule.objects.create(tenant=tenant, module=module, enabled=True, marketplace_enabled=True)
            membership = TenantMembership.objects.create(user=user, tenant=tenant)
            MembershipRole.objects.create(membership=membership, role=role)
            AppConnector.objects.create(tenant=tenant, module=module, base_url=config["urls"][code], public_url=config["urls"][code])
    else:
        from central_sync.models import CentralAccountLink
        CentralAccountLink.objects.create(central_user_id="1", user=user)
        if app == "drivesphere":
            from apps.fleet.models import VehicleBrand, VehicleModel, Vehicle
            brand = VehicleBrand.objects.create(name="Integration")
            model = VehicleModel.objects.create(brand=brand, name="Car")
            Vehicle.objects.create(brand=brand, model=model, year=2027, plate_number="PROBE-ONE", daily_rate="20.125")
        elif app == "staylux":
            from settings_app.models import PropertyProfile
            from inventory.models import UnitType, Unit
            prop = PropertyProfile.objects.create(name_en="Integration stay", currency="OMR")
            kind = UnitType.objects.create(property_profile=prop, name_en="Integration room", base_rate="20.125")
            Unit.objects.create(property_profile=prop, unit_type=kind, code="PROBE-ONE", daily_price="20.125", guest_capacity=2)
        else:
            from apps.catalog.models import Service, Item, ItemServicePrice
            service = Service.objects.create(code="probe", name="Integration wash")
            item = Item.objects.create(name="Integration garment")
            ItemServicePrice.objects.create(item=item, service=service, price="2.125")


def child(args):
    runtime = Path(args.runtime).resolve()
    config = configure(args.app, runtime)
    from django.core.management import call_command
    if args.action == "seed":
        seed(args.app, config)
    elif args.action == "serve":
        call_command("runserver", f"127.0.0.1:{config['ports'][args.app]}", use_reloader=False, verbosity=0)
    elif args.action == "inventory":
        call_command("publish_central_inventory", verbosity=0)
        call_command("flush_central_outbox", limit=10000, verbosity=0)
    elif args.action == "dispatch":
        call_command("dispatch_marketplace_bookings", verbosity=0)
    elif args.action == "finance":
        from apps.marketplace.models import MarketplaceBooking
        from apps.paymentsvc.services import create_payment, verify_and_finalize, refund_payment
        for booking in MarketplaceBooking.objects.all():
            payment, _ = create_payment({"tenant_id": booking.tenant_id, "module_code": booking.module.code, "booking_id": booking.booking_id,
                "amount": str(booking.total_amount), "currency": booking.currency, "idempotency_key": booking.booking_id + ":probe"})
            verify_and_finalize(payment)
        call_command("dispatch_payment_updates", verbosity=0)
    elif args.action == "refund":
        from apps.paymentsvc.models import CentralPayment
        from apps.paymentsvc.services import refund_payment
        for payment in CentralPayment.objects.filter(transaction_status="captured"):
            refund_payment(payment, payment.amount, "Isolated test refund", "probe-" + payment.payment_id)
        call_command("dispatch_payment_updates", verbosity=0)
    elif args.action == "complete":
        if args.app == "drivesphere":
            from apps.bookings.models import Booking
            rows, status = Booking.objects.all(), "CLOSED"
        elif args.app == "staylux":
            from bookings.models import Booking
            rows, status = Booking.objects.all(), "checked_out"
        else:
            from apps.orders.models import Order
            rows, status = Order.objects.all(), "DELIVERED"
        for row in rows:
            row.status = status
            row.save(update_fields=["status", "updated_at"])
        call_command("flush_central_outbox", limit=10000, verbosity=0)
    elif args.action == "assert-finance":
        from central_sync.models import PaymentDelivery
        if PaymentDelivery.objects.count() != 2:
            raise AssertionError("Expected one native payment and one native refund delivery")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self):
        self.opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect())

    def request(self, url, body=None, headers=None):
        request = Request(url, data=json.dumps(body).encode() if body is not None else None, headers={"Content-Type": "application/json", **(headers or {})})
        try:
            response = self.opener.open(request, timeout=45)
        except HTTPError as exc:
            response = exc
        raw = response.read().decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except ValueError:
            data = raw
        return response.code, data, response.headers


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", choices=APPS)
    parser.add_argument("--action")
    parser.add_argument("--runtime")
    args = parser.parse_args()
    if args.app:
        return child(args)
    runtime = ROOT / ".runtime" / ("probe-" + time.strftime("%Y%m%d-%H%M%S"))
    runtime.mkdir(parents=True)
    ports = {name: free_port() for name in [*APPS, "nexivo"]}
    config = {"ports": ports, "urls": {name: f"http://127.0.0.1:{port}" for name, port in ports.items()}, "secret": secrets.token_hex(32), "password": secrets.token_urlsafe(24)}
    (runtime / "config.json").write_text(json.dumps(config), encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(ROOT / ".tooling/python"), "PYTHONUNBUFFERED": "1", "DJANGO_ENV": "development"}
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    processes, logs, checks = [], [], []

    def command(app, action):
        return [sys.executable, str(Path(__file__).resolve()), "--app", app, "--action", action, "--runtime", str(runtime)]

    def run(app, action):
        result = subprocess.run(command(app, action), cwd=ROOT, env=env, capture_output=True, text=True, creationflags=flags, timeout=90)
        if result.returncode:
            (runtime / f"failure-{app}-{action}.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
            raise RuntimeError(f"{app} {action} failed; inspect its log in {runtime.name}")

    def expect(condition, name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
        print("PASS:", name, flush=True)

    try:
        for app in APPS:
            run(app, "seed")
            stream = (runtime / f"{app}.log").open("w", encoding="utf-8")
            logs.append(stream)
            processes.append(subprocess.Popen(command(app, "serve"), cwd=ROOT, env=env, stdout=stream, stderr=stream, creationflags=flags))
        client = Client()
        for app in APPS:
            for attempt in range(40):
                try:
                    client.request(config["urls"][app] + "/login/")
                    break
                except (URLError, OSError):
                    time.sleep(.5)
            else:
                raise RuntimeError(f"{app} did not start")
        for app in ("drivesphere", "staylux", "laundrex"):
            run(app, "inventory")
        node = next((ROOT / ".tooling/node").glob("node-*-win-x64/node.exe"), None)
        if node is None:
            raise RuntimeError("Portable Node runtime is missing")
        node_env = {**env, "CENTRAL_PLATFORM_API_URL": config["urls"]["central"] + "/api", "NEXIVO_SESSION_SECRET": config["secret"], "NEXT_TELEMETRY_DISABLED": "1"}
        node_env.pop("NODE_ENV", None)
        stream = (runtime / "nexivo.log").open("w", encoding="utf-8")
        logs.append(stream)
        processes.append(subprocess.Popen([str(node), str(ROOT / "nexivo/node_modules/next/dist/bin/next"), "dev", "--port", str(ports["nexivo"]), "--hostname", "127.0.0.1"], cwd=ROOT / "nexivo", env=node_env, stdout=stream, stderr=stream, creationflags=flags))
        next_url = config["urls"]["nexivo"]
        for attempt in range(60):
            try:
                code, _, _ = client.request(next_url + "/api/health")
                if code == 200:
                    break
            except (URLError, OSError):
                pass
            time.sleep(.5)
        else:
            raise RuntimeError("Nexivo did not start")
        code, _, _ = client.request(next_url + "/api/auth/register", {"fullName": "Integration Customer", "email": CUSTOMER, "password": config["password"]})
        expect(code in (200, 201), "Nexivo customer registration through Central")
        bookings = []
        for module, category in [("drivesphere", "cars"), ("staylux", "stays"), ("laundrex", "laundry")]:
            code, listing_data, _ = client.request(config["urls"]["central"] + "/api/listings/?module=" + module)
            matches = [row for row in listing_data.get("results",[]) if "Integration" in row["provider_resource_name"]]
            expect(code == 200 and len(matches) == 1, module + " inventory reaches Central")
            listing = matches[0]
            body = {"listingSlug": listing["listing_slug"], "fullName": "Integration Customer", "email": CUSTOMER, "phone": "+96890000000", "checkIn": "2027-02-01", "checkOut": "2027-02-03", "pickupDate": "2027-02-01", "returnDate": "2027-02-03", "guests": 1, "quantity": 1, "paymentMethod": "pay-online"}
            code, quoted, _ = client.request(next_url + "/api/quotes", body)
            expect(code == 200 and "quoteToken" in quoted.get("data", {}), module + " signed provider quote through Nexivo")
            code, result, _ = client.request(next_url + "/api/booking/" + category, {**body, "quoteToken": quoted["data"]["quoteToken"], "idempotencyKey": "probe-" + module})
            expect(code == 201, module + " booking persisted by Central")
            bookings.append(result["data"])
        run("central", "dispatch")
        for booking in bookings:
            code, confirmed, _ = client.request(config["urls"]["central"] + "/api/bookings/confirmation/?token=" + booking["confirmationToken"])
            expect(code == 200 and confirmed["fulfillmentStatus"] == "provider_confirmed", booking["moduleCode"] + " native booking acknowledged")
            code, checkout, _ = client.request(next_url + "/api/checkout/start", {"token": booking["confirmationToken"]})
            expect(code == 200 and checkout["data"]["charged"] is False, booking["moduleCode"] + " checkout remains simulated with zero charges")
        run("central", "finance")
        run("central", "refund")
        for app in ("drivesphere", "staylux", "laundrex"):
            run(app, "assert-finance")
            expect(True, app + " native payment/refund delivery is complete")
            run(app, "complete")
        code, history, _ = client.request(next_url + "/api/customer/bookings")
        expect(code == 200 and len(history["data"]["results"]) == 3, "Customer cookie session retrieves booking history")
        code, _, _ = client.request(next_url + "/api/customer/profile")
        expect(code == 200, "Customer cookie session retrieves profile")
        code, customer_auth, _ = client.request(config["urls"]["central"] + "/api/auth/login/", {"email": CUSTOMER, "password": config["password"]})
        code, history, _ = client.request(next_url + "/api/customer/bookings", headers={"Authorization": "Bearer " + customer_auth["accessToken"]})
        expect(code == 200 and len(history["data"]["results"]) == 3 and all(row["status"] == "completed" and row["paymentStatus"] == "refunded" for row in history["data"]["results"]), "All three final lifecycle/refund states reach Nexivo")
        code, _, _ = client.request(next_url + "/api/auth/provider-login", {"email": OWNER, "password": config["password"]})
        expect(code == 200, "Central owner signs into Nexivo")
        for app in ("drivesphere", "staylux", "laundrex"):
            app_client = Client()
            prefix = "/orders/central/" if app == "laundrex" else "/api/central/"
            code, _, headers = app_client.request(config["urls"][app] + prefix + "sso/begin/")
            expect(code == 302, app + " begins state-bound sign-in")
            state = parse_qs(urlsplit(headers["Location"]).query)["state"][0]
            code, ticket, _ = client.request(next_url + "/api/auth/sso-ticket", {"state": state, "tenantCode": "PROBE-" + app.upper(), "moduleCode": app})
            expect(code == 200, app + " Central login ticket issued")
            token = parse_qs(urlsplit(ticket["data"]["launchUrl"]).fragment)["central_sso"][0]
            code, result, _ = app_client.request(config["urls"][app] + prefix + "sso/", {"token": token})
            expect(code == 200 and result["ok"], app + " existing local account signs in")
            code, _, _ = app_client.request(config["urls"][app] + prefix + "sso/", {"token": token})
            expect(code == 403, app + " rejects ticket replay")
        (runtime / "result.json").write_text(json.dumps({"passed": checks, "realGatewayCharges": 0, "productionDataUsed": False}, indent=2), encoding="utf-8")
        print(f"Integration probe passed {len(checks)} checks. Evidence: {runtime / 'result.json'}", flush=True)
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
                else:
                    process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
        for stream in logs:
            stream.close()


if __name__ == "__main__":
    main()
