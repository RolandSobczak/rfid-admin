from typing import Annotated, List

from fastapi import APIRouter, Depends

from backend.schemas.users import UserReadSchema, UserCreationModel
from backend.schemas.tenants import TenantSchema
from backend.schemas.deployments import DeploymentSchema
from backend.repositories import KubeAPIService
from backend.schemas.users import UserReadSchema, UserCreationModel, AuthenticatedUser
from backend.permissions import RequireSuperUserToken, RequireStaffToken


router = APIRouter(prefix="/v1/deployments", tags=["deploy"])


@router.get("", response_model=List[DeploymentSchema])
async def list_deployments(
    kube_serv: Annotated[KubeAPIService, Depends(KubeAPIService)],
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
):
    return kube_serv.list_deployments()


@router.get("/{deploy}/logs", response_model=str)
async def fetch_logs(
    deploy: str,
    kube_serv: Annotated[KubeAPIService, Depends(KubeAPIService)],
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
):
    return kube_serv.fetch_deploy_logs(deploy)
