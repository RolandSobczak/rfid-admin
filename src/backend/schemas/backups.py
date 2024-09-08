import re
from typing import Union
import datetime

from pydantic import BaseModel, Field, field_validator

CRON_JOB_REGEX = r"^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$"

JOB_NAME_REGEX = r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"


class BackupSchema(BaseModel):
    id: int
    created_at: datetime.datetime
    db_name: str


class BackupCreationSchema(BaseModel):
    db_name: str


class BackupSchedulerCreationSchema(BaseModel):
    scheduler_name: str = Field(min_length=3, max_length=32, pattern=JOB_NAME_REGEX)
    app: str
    schedule: str = Field(pattern=CRON_JOB_REGEX)

    @field_validator("app")
    @classmethod
    def validate_db_exists(cls, v: str):
        from backend.repositories import DBService

        db_serv = DBService()
        if db_serv.check_db_exists(v):
            return v

        raise ValueError("Database with provided name does not exist.")

    @field_validator("scheduler_name")
    @classmethod
    def validate_scheduer_exists(cls, v: str):
        from backend.repositories import KubeAPIService

        kube_api = KubeAPIService()
        if not kube_api.check_scheduler_exists(v):
            return v

        raise ValueError("Scheduler with provided name already exists.")


class BackupSchedulerSchema(BaseModel):
    scheduler_name: str
    db_name: str
    schedule: str
