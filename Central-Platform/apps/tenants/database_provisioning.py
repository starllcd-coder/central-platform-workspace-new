import hashlib
import hmac
import json
import re
import secrets
import string
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone

from .models import TenantDatabaseConfiguration


SAFE_IDENTIFIER = re.compile(r"[^a-z0-9_]+")


def _safe_identifier(value, max_length=50):
    normalized = SAFE_IDENTIFIER.sub("_", str(value or "").strip().lower()).strip("_")
    return (normalized or "tenant")[:max_length]


def _generated_password(length=36):
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _managed_connection_values(configuration):
    engine = configuration.engine
    tenant_part = _safe_identifier(configuration.tenant.tenant_code, 30)
    module_part = _safe_identifier(configuration.module_code, 15)
    suffix = f"{tenant_part}_{module_part}"
    if engine == "postgresql":
        return {
            "host": settings.TENANT_DB_POSTGRES_HOST,
            "port": settings.TENANT_DB_POSTGRES_PORT,
            "database_name": f"tenant_{suffix}"[:63],
            "username": f"tenant_{suffix}_user"[:63],
            "ssl_mode": settings.TENANT_DB_POSTGRES_SSLMODE,
        }
    return {
        "host": settings.TENANT_DB_MYSQL_HOST,
        "port": settings.TENANT_DB_MYSQL_PORT,
        "database_name": f"tenant_{suffix}"[:64],
        "username": f"tenant_{suffix}_user"[:32],
        "ssl_mode": settings.TENANT_DB_MYSQL_SSLMODE,
    }


def _provision_managed_postgresql(configuration, password):
    import psycopg2
    from psycopg2 import sql

    connection = psycopg2.connect(
        dbname=settings.TENANT_DB_POSTGRES_ADMIN_DATABASE,
        user=settings.TENANT_DB_POSTGRES_ADMIN_USER,
        password=settings.TENANT_DB_POSTGRES_ADMIN_PASSWORD,
        host=configuration.host,
        port=configuration.port,
        sslmode=configuration.ssl_mode or "prefer",
        connect_timeout=settings.TENANT_DB_CONNECT_TIMEOUT,
    )
    connection.autocommit = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [configuration.username])
            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(configuration.username),
                        sql.Literal(password),
                    )
                )
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [configuration.database_name])
            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(configuration.database_name),
                        sql.Identifier(configuration.username),
                    )
                )
    finally:
        connection.close()


def _mysql_connection(**kwargs):
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError("PyMySQL is required for MySQL database provisioning.") from exc
    return pymysql.connect(**kwargs)


def _provision_managed_mysql(configuration, password):
    connection = _mysql_connection(
        host=configuration.host,
        port=configuration.port,
        user=settings.TENANT_DB_MYSQL_ADMIN_USER,
        password=settings.TENANT_DB_MYSQL_ADMIN_PASSWORD,
        connect_timeout=settings.TENANT_DB_CONNECT_TIMEOUT,
        autocommit=True,
    )
    database_name = configuration.database_name.replace("`", "``")
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4")
            cursor.execute(
                "CREATE USER IF NOT EXISTS %s@'%%' IDENTIFIED BY %s",
                (configuration.username, password),
            )
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON `{database_name}`.* TO %s@'%%'",
                (configuration.username,),
            )
    finally:
        connection.close()


def _validate_postgresql(configuration, password):
    import psycopg2

    connection = psycopg2.connect(
        dbname=configuration.database_name,
        user=configuration.username,
        password=password,
        host=configuration.host,
        port=configuration.port,
        sslmode=configuration.ssl_mode or "prefer",
        connect_timeout=settings.TENANT_DB_CONNECT_TIMEOUT,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    finally:
        connection.close()


def _validate_mysql(configuration, password):
    connection = _mysql_connection(
        host=configuration.host,
        port=configuration.port,
        user=configuration.username,
        password=password,
        database=configuration.database_name,
        connect_timeout=settings.TENANT_DB_CONNECT_TIMEOUT,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    finally:
        connection.close()


def validate_database_connection(configuration):
    password = configuration.get_password()
    if not password:
        raise RuntimeError("Database password could not be decrypted.")
    if configuration.engine == "postgresql":
        _validate_postgresql(configuration, password)
    else:
        _validate_mysql(configuration, password)


def _deploy_tenant_application(configuration):
    provisioner_url = settings.TENANT_APP_PROVISIONER_URL.strip()
    if not provisioner_url:
        return False
    if not settings.TENANT_APP_PROVISIONER_SECRET:
        raise RuntimeError("TENANT_APP_PROVISIONER_SECRET is not configured.")

    payload = {
        "tenant_code": configuration.tenant.tenant_code,
        "module_code": configuration.module_code,
        "database": {
            "engine": configuration.engine,
            "host": configuration.host,
            "port": configuration.port,
            "name": configuration.database_name,
            "username": configuration.username,
            "password": configuration.get_password(),
            "ssl_mode": configuration.ssl_mode,
        },
    }
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(
        settings.TENANT_APP_PROVISIONER_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    request = Request(
        provisioner_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Provisioner-Signature": signature,
        },
    )
    with urlopen(request, timeout=settings.TENANT_APP_PROVISIONER_TIMEOUT) as response:
        response_payload = json.loads(response.read().decode("utf-8") or "{}")
    if response_payload.get("status") != "ready":
        raise RuntimeError(response_payload.get("detail") or "Application deployment was not confirmed ready.")
    return True


def provision_tenant_database(configuration_id):
    configuration = TenantDatabaseConfiguration.objects.select_related("tenant").get(
        pk=configuration_id
    )
    configuration.status = "provisioning" if configuration.mode == "managed" else "validating"
    configuration.failure_reason = ""
    configuration.save(update_fields=["status", "failure_reason", "updated_at"])

    try:
        if configuration.mode == "managed":
            values = _managed_connection_values(configuration)
            for field, value in values.items():
                setattr(configuration, field, value)
            password = configuration.get_password() or _generated_password()
            configuration.set_password(password)
            configuration.save(
                update_fields=[
                    "host",
                    "port",
                    "database_name",
                    "username",
                    "password_encrypted",
                    "ssl_mode",
                    "updated_at",
                ]
            )
            if configuration.engine == "postgresql":
                _provision_managed_postgresql(configuration, password)
            else:
                _provision_managed_mysql(configuration, password)

        validate_database_connection(configuration)
        configuration.status = "deploying"
        configuration.save(update_fields=["status", "updated_at"])
        if not _deploy_tenant_application(configuration):
            configuration.status = "deployment_pending"
            configuration.failure_reason = "Database is ready; TENANT_APP_PROVISIONER_URL is not configured."
            configuration.save(update_fields=["status", "failure_reason", "updated_at"])
            return configuration

        configuration.status = "ready"
        configuration.provisioned_at = timezone.now()
        configuration.failure_reason = ""
        configuration.save(update_fields=["status", "provisioned_at", "failure_reason", "updated_at"])
        if configuration.tenant.status == "paused":
            configuration.tenant.status = configuration.activate_tenant_status
            configuration.tenant.save(update_fields=["status", "updated_at"])
    except Exception as exc:
        configuration.status = "failed"
        configuration.failure_reason = str(exc)[:1000]
        configuration.save(update_fields=["status", "failure_reason", "updated_at"])
        raise

    return configuration
