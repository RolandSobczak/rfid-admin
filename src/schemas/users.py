import datetime
from enum import Enum
from pydantic import BaseModel, PositiveInt


class TimestampedMixin:
    created_at: datetime.datetime
    updated_at: datetime.datetime


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
