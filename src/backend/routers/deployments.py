from typing import Annotated, List

from fastapi import APIRouter, Depends

from src.schemas.users import UserReadSchema, UserCreationModel
from src.schemas.tenants import TenantSchema
from src.schemas.deployments import DeploymentSchema
from src.repositories import KubeAPIService


router = APIRouter(prefix="/v1/deployments", tags=["deploy"])


@router.get("", response_model=List[DeploymentSchema])
async def list_deployments(
    kube_serv: Annotated[KubeAPIService, Depends(KubeAPIService)],
):
    return kube_serv.list_deployments()


@router.get("/{deploy}/logs", response_model=str)
async def fetch_logs(
    deploy: str,
    kube_serv: Annotated[KubeAPIService, Depends(KubeAPIService)],
):
    return kube_serv.fetch_deploy_logs(deploy)
