from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.admin.services import (get_all_superusers,
                                     grant_staff_permission,
                                     revoke_staff_permission,
                                     get_all_staff_users)
from src.apps.user.models import User
from src.apps.user.schemas import UserOutputSchema
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_superuser, check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get(
    "/superusers",
    response_model=PagedResponseSchema[UserOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_superusers(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserOutputSchema]:
    check_if_superuser(request_user)
    return get_all_superusers(db, page_params)


@admin_router.get(
    "/staff-users",
    response_model=PagedResponseSchema[UserOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_staff_users(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserOutputSchema]:
    check_if_staff(request_user)
    return get_all_staff_users(db, page_params)



@admin_router.patch(
    "/grant-staff-permissions/{user_id}", status_code=status.HTTP_200_OK
)
def grant_staff_status(
    user_id: int,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
):
    check_if_superuser(request_user)
    return grant_staff_permission(db, user_id)


@admin_router.patch(
    "/revoke-staff-permissions/{user_id}", status_code=status.HTTP_200_OK
)
def revoke_staff_status(
    user_id: int,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
):
    check_if_superuser(request_user)
    return revoke_staff_permission(db, user_id)
