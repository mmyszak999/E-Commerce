from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.admin.services import (
    get_all_superusers, grant_superuser_permission, revoke_superuser_permission
)
from src.apps.user.models import User
from src.apps.user.schemas import (UserLoginInputSchema, UserOutputSchema,
                                   UserRegisterSchema, UserUpdateSchema)
from src.apps.user.services import (authenticate, delete_single_user,
                                    get_access_token_schema, get_all_users,
                                    get_single_user, register_user,
                                    update_single_user)
from src.apps.user.routers import user_router
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_permission, check_object_permission
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user


admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get(
    "/superusers",
    response_model=PagedResponseSchema[UserOutputSchema],
    status_code=status.HTTP_200_OK
)
def get_superusers(
    db: Session = Depends(get_db), page_params: PageParams = Depends(), request_user: User = Depends(authenticate_user)
) -> PagedResponseSchema[UserOutputSchema]:
    check_permission(request_user)
    db_superusers = get_superusers(db, page_params)
    return db_superusers


@admin_router.get(
    "/grant-superuser-permissions/user/{user_id}",
    status_code=status.HTTP_200_OK
)
def grant_superuser_status(
    user_id: int, db: Session = Depends(get_db), request_user: User = Depends(authenticate_user)
):
    check_permission(request_user)
    result = grant_superuser_permission(db, user_id)
    return result


@admin_router.get(
    "/revoke-superuser-permissions/user/{user_id}",
    status_code=status.HTTP_200_OK
)
def revoke_superuser_status(
    user_id: int, db: Session = Depends(get_db), request_user: User = Depends(authenticate_user)
):
    check_permission(request_user)
    result = revoke_superuser_permission(db, user_id)
    return result







