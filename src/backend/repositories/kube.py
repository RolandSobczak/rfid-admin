from typing import List
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from backend.schemas.users import UserCreationModel, TenantProfileSchema
from backend.schemas.tenants import TenantSchema
from backend.schemas.deployments import DeploymentSchema
from backend.schemas.backups import BackupSchedulerSchema, BackupSchedulerCreationSchema
from .base import BaseService


class KubeAPIService(BaseService):
    def __init__(self):
        super().__init__()
        if self._settings.INSIDE_CLUSTER:
            config.load_incluster_config()
        else:
            config.load_kube_config()

    def _create_deployment(self, apps_v1_api, tenant: TenantProfileSchema):
        container = client.V1Container(
            name="tenant",
            image="localhost:32000/rfidio-tenant:latest",
            image_pull_policy="Always",
            ports=[client.V1ContainerPort(container_port=8000)],
            env_from=[
                client.V1EnvFromSource(
                    config_map_ref=client.V1ConfigMapEnvSource("tenant-config")
                )
            ],
            env=[
                client.V1EnvVar(
                    name="POSTGRES_DB",
                    value=tenant.slug,
                ),
                client.V1EnvVar(
                    name="TENANT_ID",
                    value=str(tenant.id),
                ),
                client.V1EnvVar(
                    name="POSTGRES_USER",
                    value_from=client.V1EnvVarSource(
                        secret_key_ref=client.V1SecretKeySelector(
                            name="db",
                            key="POSTGRES_USER",
                        )
                    ),
                ),
                client.V1EnvVar(
                    name="POSTGRES_PASSWORD",
                    value_from=client.V1EnvVarSource(
                        secret_key_ref=client.V1SecretKeySelector(
                            name="db",
                            key="POSTGRES_PASSWORD",
                        )
                    ),
                ),
                client.V1EnvVar(
                    name="RABBIT_USER",
                    value_from=client.V1EnvVarSource(
                        secret_key_ref=client.V1SecretKeySelector(
                            name="rabbit",
                            key="RABBITMQ_DEFAULT_USER",
                        )
                    ),
                ),
                client.V1EnvVar(
                    name="RABBIT_PASSWORD",
                    value_from=client.V1EnvVarSource(
                        secret_key_ref=client.V1SecretKeySelector(
                            name="rabbit",
                            key="RABBITMQ_DEFAULT_PASS",
                        )
                    ),
                ),
            ],
        )
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={"app": "tenant", "tenant": tenant.slug}
            ),
            spec=client.V1PodSpec(containers=[container]),
        )
        spec = client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": "tenant", "tenant": tenant.slug}
            ),
            template=template,
        )
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=tenant.slug, labels={"app": "tenant", "tenant": tenant.slug}
            ),
            spec=spec,
        )
        # Creation of the Deployment in specified namespace
        # (Can replace "default" with a namespace you may have created)
        apps_v1_api.create_namespaced_deployment(
            namespace=self._settings.NAMESPACE, body=deployment
        )

    def _create_service(self, tenant: TenantProfileSchema):
        core_v1_api = client.CoreV1Api()
        body = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=tenant.slug),
            spec=client.V1ServiceSpec(
                selector={"tenant": tenant.slug, "app": "tenant"},
                ports=[client.V1ServicePort(port=8000, target_port=8000)],
                type="LoadBalancer",
            ),
        )
        # Creation of the Deployment in specified namespace
        # (Can replace "default" with a namespace you may have created)
        core_v1_api.create_namespaced_service(
            namespace=self._settings.NAMESPACE, body=body
        )

    def _create_ingress(self, networking_v1_api, tenant: TenantProfileSchema):
        body = client.V1Ingress(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            metadata=client.V1ObjectMeta(
                name=tenant.slug,
                annotations={
                    "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                    "nginx.ingress.kubernetes.io/use-regex": "true",
                },
            ),
            spec=client.V1IngressSpec(
                rules=[
                    client.V1IngressRule(
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path=f"/{tenant.slug}(/|$)(.*)",
                                    path_type="ImplementationSpecific",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            port=client.V1ServiceBackendPort(
                                                number=8000,
                                            ),
                                            name=tenant.slug,
                                        )
                                    ),
                                )
                            ]
                        ),
                    )
                ]
            ),
        )
        networking_v1_api.create_namespaced_ingress(
            namespace=self._settings.NAMESPACE, body=body
        )

    def deploy_tenant(self, tenant: TenantProfileSchema):
        apps_v1_api = client.AppsV1Api()
        networking_v1_api = client.NetworkingV1Api()

        self._create_deployment(apps_v1_api, tenant)
        self._create_service(tenant)
        self._create_ingress(networking_v1_api, tenant)

    def destroy_tenant(self, tenant: TenantSchema):
        k8s_apps_v1 = client.AppsV1Api()
        k8s_apps_v1.delete_namespaced_deployment(tenant.slug, self._settings.NAMESPACE)
        core_v1_api = client.CoreV1Api()
        core_v1_api.delete_namespaced_service(tenant.slug, self._settings.NAMESPACE)
        networking_v1_api = client.NetworkingV1Api()
        networking_v1_api.delete_namespaced_ingress(
            tenant.slug, self._settings.NAMESPACE
        )

    def list_raw_deployments(self) -> List[dict]:
        api_instance = client.AppsV1Api()
        api_response = api_instance.list_namespaced_deployment(namespace="rfid-main")
        return [
            {"name": deploy.metadata.name, "labels": deploy.metadata.labels}
            for deploy in api_response.items
        ]

    def read_status(self, pod_name: str) -> List[dict]:
        try:
            api_instance = client.CoreV1Api()
            api_response = api_instance.read_namespaced_pod_status(
                pod_name, self._settings.NAMESPACE, pretty=True
            )
            return [
                {
                    "name": container.name,
                    "ready": container.ready,
                }
                for container in api_response.status.container_statuses
            ]
        except ApiException as e:
            print(
                "Exception when calling CoreV1Api->read_namespaced_pod_status: %s\n" % e
            )

    def load_logs(self, pod_name: str):
        api_instance = client.CoreV1Api()
        pod_logs = api_instance.read_namespaced_pod_log(
            name=pod_name, namespace=self._settings.NAMESPACE
        )
        return pod_logs

    def get_deploy_pods(self, label_selector: str) -> List[dict]:
        api_instance = client.CoreV1Api()
        pods = api_instance.list_namespaced_pod(
            namespace=self._settings.NAMESPACE, label_selector=label_selector
        )

        out = []
        for pod in pods.items:
            pod_name = pod.metadata.name
            containers = [
                {"name": container.name, "image": container.image}
                for container in pod.spec.containers
            ]
            out.append(
                {
                    "name": pod_name,
                    "containers": containers,
                }
            )
        return out

    def list_deployments(self) -> List[DeploymentSchema]:
        raw_deployments = self.list_raw_deployments()
        deployments = []
        for deploy in raw_deployments:
            deploy_name = deploy["name"]
            app = deploy["labels"]["app"]
            pods_selector = ""
            if deploy["labels"].get("tenant"):
                tenant = deploy["labels"]["tenant"]
                pods_selector = f"app=tenant,tenant={tenant}"
            else:
                pods_selector = f"app={deploy_name}"

            pods = self.get_deploy_pods(pods_selector)
            if len(pods) > 0:
                containers_status = self.read_status(pods[0]["name"])
                if len(containers_status) > 0:
                    containers_ready = all(
                        [container.get("ready") for container in containers_status]
                    )
                    deployments.append(
                        DeploymentSchema(
                            name=deploy_name,
                            ready=containers_ready,
                            containers=pods[0]["containers"],
                        )
                    )

        return deployments

    def fetch_deploy_logs(self, deploy_name: str):
        api_instance = client.AppsV1Api()
        deploy = api_instance.read_namespaced_deployment(
            deploy_name,
            self._settings.NAMESPACE,
        )
        labels = deploy.metadata.labels
        pods_selector = ""
        if tenant := labels.get("tenant"):
            pods_selector = f"app=tenant,tenant={tenant}"
        else:
            pods_selector = f"app={deploy_name}"

        pods = self.get_deploy_pods(pods_selector)
        logs = self.load_logs(pods[0]["name"])
        return logs

    @staticmethod
    def _resolve_cron_wildcard(val: int) -> str:
        if val < 0:
            return "*"
        return str(val)

    def schedule_backup(self, schema: BackupSchedulerSchema):
        job_template = client.V1JobTemplateSpec(
            metadata=client.V1ObjectMeta(
                namespace=self._settings.NAMESPACE,
            ),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(namespace=self._settings.NAMESPACE),
                    spec=client.V1PodSpec(
                        restart_policy="OnFailure",
                        containers=[
                            client.V1Container(
                                name="sender",
                                image="localhost:32000/rfidio-mq-sender:latest",
                                image_pull_policy="Always",
                                env=[
                                    client.V1EnvVar(
                                        name="DB_NAME",
                                        value=schema.app,
                                    )
                                ],
                            )
                        ],
                    ),
                )
            ),
        )

        cronjob = client.V1CronJob(
            api_version="batch/v1",
            kind="CronJob",
            metadata=client.V1ObjectMeta(
                name=schema.scheduler_name, namespace=self._settings.NAMESPACE
            ),
            spec=client.V1CronJobSpec(
                schedule=schema.schedule,
                job_template=job_template,
            ),
        )

        batch_v1 = client.BatchV1Api()
        batch_v1.create_namespaced_cron_job(
            namespace=self._settings.NAMESPACE, body=cronjob
        )

    def list_cron_jobs(self) -> List[BackupSchedulerSchema]:
        api_instance = client.BatchV1Api()
        api_response = api_instance.list_namespaced_cron_job(self._settings.NAMESPACE)
        out = []
        for cron in api_response.items:
            name = cron.metadata.name
            schedule = cron.spec.schedule
            db_name_env = list(
                filter(
                    lambda env: env.name == "DB_NAME",
                    cron.spec.job_template.spec.template.spec.containers[0].env,
                )
            )[0]
            db_name = db_name_env.value
            out.append(
                BackupSchedulerSchema(
                    scheduler_name=name,
                    db_name=db_name,
                    schedule=schedule,
                )
            )
        return out

    def remove_cron_job(self, job_name: str):
        api_instance = client.BatchV1Api()
        api_response = api_instance.delete_namespaced_cron_job(
            job_name,
            self._settings.NAMESPACE,
        )

    def get_deploy_backups(self) -> List[BackupSchedulerSchema]:
        pass
