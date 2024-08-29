import re
from typing import Union
import datetime

from pydantic import BaseModel, Field, field_validator

CRON_JOB_REGEX = re.compile(
    r"^(\*|[0-5]?\d)( \*| [01]?\d|2[0-3])( \*| [01]?\d|3[01])( \*| [0-9]|1[0-2])( \*| [0-6])$"
)


class BackupSchema(BaseModel):
    id: int
    created_at: datetime.datetime
    db_name: str


class BackupCreationSchema(BaseModel):
    db_name: str


class BackupSchedulerCreationSchema(BaseModel):
    scheduler_name: str = Field(min_length=3, max_length=32)
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


class BackupSchedulerSchema(BaseModel):
    scheduler_name: str
    db_name: str
    schedule: str
