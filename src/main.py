import sys
import datetime

sys.path.append("..")

from src.schemas.users import (
    UserCreationModel,
    TenantCreationModel,
    TenantType,
    Lang,
    UserReadSchema,
    TenantProfileSchema,
)
from src.repositories import TenantService


def main():
    user_data = UserCreationModel(
        email="rolandsobczak10@gmail.com",
        password="Elektryk1@",
        first_name="Roland",
        last_name="Sobczak",
        tenant=TenantCreationModel(
            type=TenantType.HOTEL, lang=Lang.PL, name="new-tenant"
        ),
    )
    user_data_destroy = UserReadSchema(
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        id=38,
        email="rolandsobczak10@gmail.com",
        first_name="Roland",
        last_name="Sobczak",
        tenant=TenantProfileSchema(
            id=38,
            name="new-tenant",
            slug="new-tenant",
            type=TenantType.HOTEL,
            lang=Lang.PL,
        ),
        is_superuser=True,
        is_confirmed=True,
        is_active=True,
    )
    tenant = TenantService()
    tenant.destroy(user_data_destroy)
    # tenant.deploy(user_data)


if __name__ == "__main__":
    main()
