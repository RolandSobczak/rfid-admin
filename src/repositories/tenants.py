from schemas.users import TenantProfileSchema, UserCreationModel
from .auth_api import AuthAPIService
from .database import DBService
from .kube import KubeAPIService


class TenantService:
    def __init__(self):
        self._db_serv = DBService()
        self._auth_serv = AuthAPIService()
        self._kube_serv = KubeAPIService()

    def deploy(self, user_data: UserCreationModel) -> int:
        user = self._auth_serv.register_user(user_data)
        self._db_serv.create_database(user.tenant.slug)
        self._kube_serv.deploy_tenant(user.tenant)
        return user.tenant.id

    def destroy(self, tenant: TenantProfileSchema):
        self._db_serv.destroy_tenant(tenant.owner.id)
        self._db_serv.drop_database(tenant.slug)
        self._kube_serv.destroy_tenant(tenant)
