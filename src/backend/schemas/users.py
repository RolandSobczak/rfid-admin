from typing import List
import datetime
from enum import Enum

from pydantic import BaseModel, PositiveInt

from .mixins import TimestampedMixin


class UserType(Enum):
    ROOT = "root"
    IAM = "iam"
    SERVICE = "service"


class TenantType(Enum):
    HOTEL = "hotel"
    WAREHOUSE = "warehouse"


class Lang(Enum):
    PL = "pl-PL"


class TenantCreationModel(BaseModel):
    class Config:
        use_enum_values = True

    type: TenantType
    lang: Lang
    name: str


class UserCreationModel(BaseModel):
    class Config:
        use_enum_values = True

    email: str
    password: str
    first_name: str
    last_name: str
    tenant: TenantCreationModel


class TenantProfileSchema(BaseModel):
    id: int
    name: str
    slug: str
    type: TenantType
    lang: Lang


class UserReadSchema(BaseModel, TimestampedMixin):
    id: PositiveInt
    email: str
    first_name: str
    last_name: str
    tenant: TenantProfileSchema
    is_superuser: bool
    is_confirmed: bool
    is_active: bool


class AuthenticatedUser(BaseModel):
    id: int
    username: str
    scope: list[str]
    type: UserType
    tenant_id: int
    tenant_name: str
    allowed_locations: List[int]
    permissions: List[str]
