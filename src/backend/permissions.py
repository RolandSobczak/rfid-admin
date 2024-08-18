from functools import cache
from abc import ABC, abstractmethod
from typing import Annotated, Any, Generator, Optional, Sequence, List
from enum import Enum

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError

from backend.schemas.users import AuthenticatedUser, UserType
from backend.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
)


class InvalidTokenTypeException(Exception):
    """Raised when token scope contain unknown token type.

    Valid token types:
        - root
        - iam
        - service #long term tokens for external services
    """


class AccessToken:
    def __init__(self, token: str):
        self._token = token
        self._settings = Settings()
        self.scopes = None

    def decode_access_token(self) -> dict:
        payload = jwt.decode(
            self._token,
            self._settings.PUBLIC_KEY,
            algorithms=["RS256"],
        )
        return payload

    def parse_user(self) -> AuthenticatedUser:
        payload = self.decode_access_token()
        username = payload.get("sub")
        user_id = payload.get("iss")
        token_scopes: list[str] = payload.get("scope", "").split()
        self.scopes = token_scopes

        user_type = None
        tenant_id = None
        tenant_name = None

        if "type:root" in token_scopes:
            user_type = UserType.ROOT
        elif "type:iam" in token_scopes:
            user_type = UserType.IAM
        elif "type:service" in token_scopes:
            user_type = UserType.SERVICE
        else:
            raise InvalidTokenTypeException

        if not any(["tenant" in scope for scope in token_scopes]):
            raise InvalidTokenTypeException

        if not any(["tenant_name" in scope for scope in token_scopes]):
            raise InvalidTokenTypeException

        allowed_locations = []
        permissions = []

        for scope in token_scopes:
            if scope.startswith("tenant_name"):
                tenant_name = scope.split(":")[-1]
            elif scope.startswith("tenant") and not scope.startswith("tenant_name"):
                raw_tenant_id = scope.split(":")[-1]
                if raw_tenant_id == "null":
                    tenant_id = -1
                else:
                    tenant_id = int(raw_tenant_id)
            elif scope.startswith("location") and not scope.startswith("locations"):
                allowed_locations.append(int(scope.split(":")[-1]))
            elif scope.startswith("type"):
                continue
            else:
                permissions.append(scope)

        return AuthenticatedUser(
            id=user_id,
            username=username,
            scope=token_scopes,
            type=user_type,
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            allowed_locations=allowed_locations,
            permissions=permissions,
        )


class BaseAuthDependency(ABC):
    _settings = Settings()

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    def _get_user(self, raw_token: str) -> AuthenticatedUser:
        try:
            self.token = AccessToken(raw_token)
            user = self.token.parse_user()
            return user
        except ExpiredSignatureError:
            print("Expired token provided.")
            raise self.credentials_exception
        except InvalidSignatureError:
            print("Token with unknown signature has been provided")
            raise self.credentials_exception
        except DecodeError:
            print("Invalid token provided.")
            raise self.credentials_exception
        except InvalidTokenTypeException:
            print("User provided token with unknown type")
            raise self.credentials_exception

    @abstractmethod
    def _validate_permissions(self, user: AuthenticatedUser, token: str):
        pass

    def __call__(
        self,
        raw_token: Annotated[str, Depends(oauth2_scheme)],
    ) -> AuthenticatedUser:
        """This method check if user has sufficient permissions to perform action.

        @param logger:
        @param token:
        @param tenant_id:
        @return:
        """

        user = self._get_user(raw_token)
        self._validate_permissions(user, raw_token)

        return user


class RequireRootToken(BaseAuthDependency):
    def _validate_permissions(self, user: AuthenticatedUser, *args, **kwargs):
        if user.type != UserType.ROOT:
            raise self.credentials_exception


class RequireStaffToken(BaseAuthDependency):
    def _validate_permissions(self, *args, **kwargs):
        if "staff:1" in self.token.scopes:
            return
        raise self.credentials_exception


class RequireSuperUserToken(BaseAuthDependency):
    def _validate_permissions(self, *args, **kwargs):
        if "super:1" in self.token.scopes and "staff:1" in self.token.scopes:
            return
        raise self.credentials_exception
