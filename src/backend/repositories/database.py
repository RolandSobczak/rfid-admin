from typing import Optional, List
from fastapi import HTTPException

from sqlalchemy import create_engine, text
from backend.schemas.tenants import TenantSchema, OwnerProfile
from sqlalchemy_utils.functions import database_exists, create_database, drop_database
from sqlalchemy.exc import SQLAlchemyError

from .base import BaseService


class DBService(BaseService):
    def _create_extensions(self, target_conn_str: str):
        engine = create_engine(target_conn_str, echo=True)

        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION pg_trgm"))

    def create_database(self, db_name: str):
        target_conn_str = self._settings.DBHOST + db_name

        if not database_exists(target_conn_str):
            create_database(target_conn_str)

    def destroy_tenant(self, user_id: int):
        engine = create_engine(self._settings.DBHOST + "auth", echo=True)

        try:
            with engine.connect() as conn:
                with conn.begin():  # Start a transaction
                    conn.execute(
                        text("DELETE FROM refresh_tokens WHERE user_id = :user_id"),
                        {"user_id": user_id},
                    )
                    conn.execute(
                        text("DELETE FROM users WHERE id = :user_id"),
                        {"user_id": user_id},
                    )
        except SQLAlchemyError as e:
            print(f"An error occurred: {e}")

    # def get_user_by_email(self, user_email):
    #     pass

    def drop_database(self, db_name: str):
        if database_exists(self._settings.DBHOST + db_name):
            drop_database(self._settings.DBHOST + db_name)

    def get_db_list(self) -> List[str]:
        engine = create_engine(self._settings.DBHOST, echo=True)

        with engine.connect() as conn:
            with conn.begin():
                stmt = """
                        SELECT datname
                        FROM pg_database
                        WHERE datistemplate = false;
                        """
                res = conn.execute(text(stmt))
                if res is None:
                    return []

                return [row[0] for row in res]

    def get_tenant_by_id(self, tenant_id: int) -> Optional[TenantSchema]:
        engine = create_engine(self._settings.DBHOST + "auth", echo=True)

        with engine.connect() as conn:
            with conn.begin():
                stmt = """SELECT
                            t.created_at,
                            t.updated_at,
                            t.id,
                            t.name,
                            t.slug,
                            t.type,
                            u.id,
                            u.email
                        FROM tenants t
                        INNER JOIN users u ON u.id = t.owner_id
                        WHERE t.id = :tenant_id
                        """
                res = conn.execute(text(stmt), {"tenant_id": tenant_id}).fetchone()
                if res is None:
                    return None
                (
                    created_at,
                    updated_at,
                    tenant_id,
                    tenant_name,
                    tenant_slug,
                    tenant_type,
                    owner_id,
                    owner_email,
                ) = res
                return TenantSchema(
                    created_at=created_at,
                    updated_at=updated_at,
                    id=tenant_id,
                    name=tenant_name,
                    slug=tenant_slug,
                    type=tenant_type,
                    owner=OwnerProfile(
                        id=owner_id,
                        email=owner_email,
                    ),
                    healthy=False,
                )

    def get_one_or_404(self, tenant_id: int) -> TenantSchema:
        tenant = self.get_tenant_by_id(tenant_id)
        if tenant is None:
            raise HTTPException(
                status_code=404,
                detail="Tenant not found",
            )

        return tenant

    def get_tenant_by_slug(self, tenant_slug: str) -> Optional[TenantSchema]:
        engine = create_engine(self._settings.DBHOST + "auth", echo=True)

        with engine.connect() as conn:
            with conn.begin():
                stmt = """SELECT
                            t.created_at,
                            t.updated_at,
                            t.id,
                            t.name,
                            t.slug,
                            t.type,
                            u.id,
                            u.email
                        FROM tenants t
                        INNER JOIN users u ON u.id = t.owner_id
                        WHERE t.slug = :tenant_slug
                        """
                res = conn.execute(text(stmt), {"tenant_slug": tenant_slug}).fetchone()
                if res is None:
                    return None
                (
                    created_at,
                    updated_at,
                    tenant_id,
                    tenant_name,
                    tenant_slug,
                    tenant_type,
                    owner_id,
                    owner_email,
                ) = res
                return TenantSchema(
                    created_at=created_at,
                    updated_at=updated_at,
                    id=tenant_id,
                    name=tenant_name,
                    slug=tenant_slug,
                    type=tenant_type,
                    owner=OwnerProfile(
                        id=owner_id,
                        email=owner_email,
                    ),
                    healthy=False,
                )

    def get_tenants_list(self) -> List[TenantSchema]:
        engine = create_engine(self._settings.DBHOST + "auth", echo=True)

        with engine.connect() as conn:
            with conn.begin():
                stmt = """SELECT
                            t.created_at,
                            t.updated_at,
                            t.id,
                            t.name,
                            t.slug,
                            t.type,
                            u.id,
                            u.email
                        FROM tenants t
                        INNER JOIN users u ON u.id = t.owner_id
                        """
                res = conn.execute(text(stmt))

                if res is None:
                    return None

                out = []
                for row in res:
                    (
                        created_at,
                        updated_at,
                        tenant_id,
                        tenant_name,
                        tenant_slug,
                        tenant_type,
                        owner_id,
                        owner_email,
                    ) = row
                    tenant = TenantSchema(
                        created_at=created_at,
                        updated_at=updated_at,
                        id=tenant_id,
                        name=tenant_name,
                        slug=tenant_slug,
                        type=tenant_type,
                        owner=OwnerProfile(
                            id=owner_id,
                            email=owner_email,
                        ),
                        healthy=False,
                    )
                    out.append(tenant)

                return out
