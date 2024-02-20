from typing import Union

from fastapi import BackgroundTasks, Depends, Request, Response, status
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.orders.schemas import OrderOutputSchema
from src.apps.orders.services.order_services import get_all_user_orders
from src.apps.user.models import User
from src.apps.user.schemas import (
    UserInfoOutputSchema,
    UserLoginInputSchema,
    UserOutputSchema,
    UserRegisterSchema,
    UserUpdateSchema,
)
from src.apps.user.services.user_services import (
    delete_single_user,
    get_access_token_schema,
    get_all_users,
    get_single_user,
    register_user,
    update_single_user,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post(
    "/register", response_model=UserOutputSchema, status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserRegisterSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> UserOutputSchema:
    return register_user(db, user, background_tasks)


@user_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=AccessTokenOutputSchema
)
def login_user(
    user_login_schema: UserLoginInputSchema,
    auth_jwt: AuthJWT = Depends(),
    db: Session = Depends(get_db),
) -> AccessTokenOutputSchema:
    return get_access_token_schema(user_login_schema, db, auth_jwt)


@user_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(authenticate_user)],
    response_model=UserOutputSchema,
)
def get_logged_user(
    request_user: User = Depends(authenticate_user),
) -> UserOutputSchema:
    return UserOutputSchema.from_orm(request_user)


@user_router.get(
    "/",
    response_model=PagedResponseSchema[UserOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_users(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserOutputSchema]:
    check_if_staff(request_user)
    return get_all_users(db, page_params, request.query_params.multi_items())


@user_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[UserInfoOutputSchema, UserOutputSchema]:
    if request_user.is_staff:
        return get_single_user(db, user_id)
    return get_single_user(db, user_id, output_schema=UserInfoOutputSchema)


@user_router.get(
    "/{user_id}/orders",
    response_model=PagedResponseSchema[OrderOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_user_orders(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[OrderOutputSchema]:
    check_if_staff(request_user)
    return get_all_user_orders(
        db, user_id, page_params, request.query_params.multi_items()
    )


@user_router.patch(
    "/{user_id}",
    response_model=UserOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_user(
    user_id: str,
    user: UserUpdateSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> UserOutputSchema:
    check_if_staff_or_owner(request_user, "id", user_id)
    return update_single_user(db, user, user_id)


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    check_if_staff(request_user)
    delete_single_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
