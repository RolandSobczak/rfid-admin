from src.schemas.users import UserReadSchema

from sqlalchemy import create_engine, text
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

    def get_user_by_email(self, user_email):
        pass

    def drop_database(self, db_name: str):
        if not database_exists(self._settings.DBHOST + db_name):
            drop_database(self._settings.DBHOST + db_name)
