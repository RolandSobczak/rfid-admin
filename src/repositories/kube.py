from kubernetes import client, config

from src.schemas.users import UserCreationModel, TenantProfileSchema
from src.schemas.tenants import TenantSchema
from .base import BaseService


class KubeAPIService(BaseService):
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
            metadata=client.V1ObjectMeta(name=tenant.slug),
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
        config.load_kube_config()
        apps_v1_api = client.AppsV1Api()
        networking_v1_api = client.NetworkingV1Api()

        self._create_deployment(apps_v1_api, tenant)
        self._create_service(tenant)
        self._create_ingress(networking_v1_api, tenant)

    def destroy_tenant(self, tenant: TenantSchema):
        config.load_kube_config()
        k8s_apps_v1 = client.AppsV1Api()
        k8s_apps_v1.delete_namespaced_deployment(tenant.slug, self._settings.NAMESPACE)
        core_v1_api = client.CoreV1Api()
        core_v1_api.delete_namespaced_service(tenant.slug, self._settings.NAMESPACE)
        networking_v1_api = client.NetworkingV1Api()
        networking_v1_api.delete_namespaced_ingress(
            tenant.slug, self._settings.NAMESPACE
        )
