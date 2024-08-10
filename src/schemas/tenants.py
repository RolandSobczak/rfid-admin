from pydantic import BaseModel

from .mixins import TimestampedMixin
from .users import TenantType


class OwnerProfile(BaseModel):
    id: int
    email: str


class TenantSchema(BaseModel, TimestampedMixin):
    id: int
    owner: OwnerProfile
    name: str
    slug: str
    type: TenantType
