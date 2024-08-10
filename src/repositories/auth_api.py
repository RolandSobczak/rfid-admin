import httpx

from src.schemas.users import UserCreationModel, UserReadSchema
from .base import BaseService


class AuthAPIService(BaseService):
    def register_user(self, schema: UserCreationModel) -> UserReadSchema:
        with httpx.Client(base_url=self._settings.AUTH_API_HOST) as client:
            res = client.post("/users", json=schema.model_dump())
            if res.status_code != 201:
                raise RuntimeError(f"AUTH API raises {res.status_code} status code")

            user = UserReadSchema(**res.json())
            return user
