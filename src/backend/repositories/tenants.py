import httpx
from jinja2 import Template
from typing import List

from backend.schemas.users import TenantProfileSchema, UserCreationModel
from backend.schemas.tenants import TenantSchema
from .auth_api import AuthAPIService
from .database import DBService
from .kube import KubeAPIService
from .base import BaseService


class TenantService(BaseService):
    def __init__(self):
        super().__init__()

        self._db_serv = DBService()
        self._auth_serv = AuthAPIService()
        self._kube_serv = KubeAPIService()

    async def check_healthy(self, tenant: TenantSchema) -> bool:
        template = Template(self._settings.TENANT_API_TEMPLATE)
        tenant_url = template.render(
            {
                "tenant_id": tenant.id,
                "tenant_slug": tenant.slug,
            }
        )

        async with httpx.AsyncClient(base_url=tenant_url) as client:
            try:
                res = await client.get("/healthcheck")
                if res.status_code == 200:
                    return True
                return False
            except httpx.HTTPError:
                return False

    async def list_tenants(self) -> List[TenantSchema]:
        db_tenants = self._db_serv.get_tenants_list()
        for tenant in db_tenants:
            is_healthy = await self.check_healthy(tenant)
            tenant.healthy = is_healthy
        return db_tenants

    def deploy(self, user_data: UserCreationModel) -> int:
        user = self._auth_serv.register_user(user_data)
        self._db_serv.create_database(user.tenant.slug)
        self._kube_serv.deploy_tenant(user.tenant)
        return user.tenant.id

    def destroy(self, tenant: TenantProfileSchema):
        self._db_serv.destroy_tenant(tenant.owner.id)
        self._db_serv.drop_database(tenant.slug)
        self._kube_serv.destroy_tenant(tenant)
