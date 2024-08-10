from typing import Annotated, List

from fastapi import APIRouter, Depends

from src.schemas.users import UserReadSchema, UserCreationModel
from src.schemas.tenants import TenantSchema
from src.repositories import TenantService, DBService


router = APIRouter(prefix="/v1/tenants", tags=["tenants"])


@router.post("", response_model=TenantSchema, status_code=201)
async def deploy_tenant(
    schema: UserCreationModel,
    tenant_serv: Annotated[TenantService, Depends(TenantService)],
    database_serv: Annotated[DBService, Depends(DBService)],
):
    tenant_id = tenant_serv.deploy(schema)
    return database_serv.get_tenant_by_id(tenant_id)


@router.get("", response_model=List[TenantSchema])
async def list_tenants(
    database_serv: Annotated[DBService, Depends(DBService)],
):
    return database_serv.get_tenants_list()


@router.get("/{tenant_id}", response_model=TenantSchema)
async def retrieve_tenant(
    tenant_id: int,
    database_serv: Annotated[DBService, Depends(DBService)],
):
    return database_serv.get_one_or_404(tenant_id)


@router.delete("/{tenant_id}", status_code=204, response_model=None)
async def destroy_tenant(
    tenant_id: int,
    tenant_serv: Annotated[TenantService, Depends(TenantService)],
    database_serv: Annotated[DBService, Depends(DBService)],
):
    tenant = database_serv.get_one_or_404(tenant_id)
    tenant_serv.destroy(tenant)
    return tenant
