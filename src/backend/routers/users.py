from typing import Annotated

from fastapi import APIRouter, Depends

from backend.repositories import DBService
from backend.schemas.users import AuthenticatedUser
from backend.permissions import RequireSuperUserToken

router = APIRouter(prefix="/v1/users", tags=["backups"])


@router.delete("/{user_id}", response_model=None)
async def destroy_user(
    user_id: int,
    db_serv: Annotated[DBService, Depends(DBService)],
    user: Annotated[AuthenticatedUser, Depends(RequireSuperUserToken())],
):
    db_serv.destroy_tenant(user_id)
