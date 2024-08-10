from schemas.users import UserReadSchema
from .auth_api import AuthAPIService
from .database import DBService
from .kube import KubeAPIService


class TenantService:
    def __init__(self):
        self._db_serv = DBService()
        self._auth_serv = AuthAPIService()
        self._kube_serv = KubeAPIService()

    def deploy(self, user_data: DBService):
        user = self._auth_serv.register_user(user_data)
        self._db_serv.create_database(user.tenant.slug)
        self._kube_serv.deploy_tenant(user.tenant)

    def destroy(self, user: UserReadSchema):
        self._db_serv.destroy_tenant(user.id)
        self._db_serv.drop_database(user.tenant.slug)
        self._kube_serv.destroy_tenant(user.tenant)
