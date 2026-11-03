from celery import shared_task

from .database_provisioning import provision_tenant_database


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="apps.tenants.tasks.provision_tenant_database_task",
)
def provision_tenant_database_task(self, configuration_id):
    configuration = provision_tenant_database(configuration_id)
    return {"configuration_id": configuration.id, "status": configuration.status}
