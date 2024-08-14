from typing import Union
import datetime
from pydantic import BaseModel


class BackupSchema(BaseModel):
    id: int
    created_at: datetime.datetime
    db_name: str


class BackupCreationSchema(BaseModel):
    db_name: str


class BackupSchedulerCreationSchema(BaseModel):
    scheduler_name: str
    app: str
    schedule: str


class BackupSchedulerSchema(BaseModel):
    scheduler_name: str
    db_name: str
    schedule: str
