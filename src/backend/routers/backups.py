import datetime
import os
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from backend.schemas.users import UserReadSchema, UserCreationModel
from backend.schemas.tenants import TenantSchema
from backend.schemas.backups import (
    BackupSchema,
    BackupCreationSchema,
    BackupSchedulerSchema,
    BackupSchedulerCreationSchema,
)
from backend.repositories import MQService, KubeAPIService, DBService
from backend.schemas.users import AuthenticatedUser
from backend.permissions import RequireStaffToken
from backend.settings import Settings

router = APIRouter(prefix="/v1/backups", tags=["backups"])


@router.get("/schedulers")  # , response_model=List[BackupSchema])
async def list_schedulers(
    kube: Annotated[KubeAPIService, Depends(KubeAPIService)],
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
):
    return kube.list_cron_jobs()


@router.post("/schedulers", response_model=BackupSchedulerSchema, status_code=201)
async def create_scheduler(
    schema: BackupSchedulerCreationSchema,
    db: Annotated[DBService, Depends(DBService)],
    kube: Annotated[KubeAPIService, Depends(KubeAPIService)],
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
):
    if schema.app != "auth":
        db_tenant = db.get_tenant_by_slug(schema.app)
        if db_tenant is None:
            raise HTTPException(
                status_code=422,
                detail="Tenant with provided slug does not exist!",
            )

    kube.schedule_backup(schema)
    return BackupSchedulerSchema(
        scheduler_name=schema.scheduler_name,
        db_name=schema.app,
        schedule=schema.schedule,
    )


@router.delete("/schedulers/{scheduler_name}", response_model=None, status_code=204)
async def destroy_scheduler(
    scheduler_name: str,
    kube: Annotated[KubeAPIService, Depends(KubeAPIService)],
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
):
    kube.remove_cron_job(scheduler_name)


@router.post("", response_model=BackupSchema)
async def request_backup(
    schema: BackupCreationSchema,
    mq: Annotated[MQService, Depends(MQService)],
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
):
    mq.request_backup(schema.db_name)
    return BackupSchema(
        id=1, created_at=datetime.datetime.now(), db_name=schema.db_name
    )


@router.post("", response_model=BackupSchema)
async def last_backups(
    schema: BackupCreationSchema,
    mq: Annotated[MQService, Depends(MQService)],
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
):
    pass


@router.get("", response_model=List[str])
async def list_by_db(
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
    settings: Annotated[Settings, Depends(Settings)],
):
    return os.listdir(settings.BACKUP_DIR)


@router.get("/{db_name}", response_model=List[str])
async def list_db_backups(
    db_name: str,
    user: Annotated[AuthenticatedUser, Depends(RequireStaffToken())],
    settings: Annotated[Settings, Depends(Settings)],
):
    try:
        return os.listdir(f"{settings.BACKUP_DIR}/{db_name}")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="backups folder with provided name not found",
        )
