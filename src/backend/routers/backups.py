import datetime
import os
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from src.schemas.users import UserReadSchema, UserCreationModel
from src.schemas.tenants import TenantSchema
from src.schemas.backups import (
    BackupSchema,
    BackupCreationSchema,
    BackupSchedulerSchema,
    BackupSchedulerCreationSchema,
)
from src.repositories import MQService, KubeAPIService, DBService


router = APIRouter(prefix="/v1/backups", tags=["backups"])


@router.get("/schedulers")  # , response_model=List[BackupSchema])
async def list_schedulers(kube: Annotated[KubeAPIService, Depends(KubeAPIService)]):
    return kube.list_cron_jobs()


@router.post("/schedulers", response_model=BackupSchedulerSchema, status_code=201)
async def create_scheduler(
    schema: BackupSchedulerCreationSchema,
    db: Annotated[DBService, Depends(DBService)],
    kube: Annotated[KubeAPIService, Depends(KubeAPIService)],
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
        db_name=schema.app,
        schedule=schema.schedule,
    )


@router.post("", response_model=BackupSchema)
async def request_backup(
    schema: BackupCreationSchema,
    mq: Annotated[MQService, Depends(MQService)],
):
    mq.request_backup(schema.db_name)
    return schema


@router.post("", response_model=BackupSchema)
async def last_backups(
    schema: BackupCreationSchema,
    mq: Annotated[MQService, Depends(MQService)],
):
    pass


@router.get("", response_model=List[str])
async def list_by_db():
    return os.listdir("backups")


@router.get("/{db_name}", response_model=List[str])
async def list_db_backups(db_name: str):
    try:
        return os.listdir(f"backups/{db_name}")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="backups folder with provided name not found",
        )
