from fastapi import Depends, Response, status, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.emails.services import send_confirmation_mail_change_email
from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.orders.schemas import OrderOutputSchema
from src.apps.user.models import User
from src.apps.user.schemas import (UserLoginInputSchema, UserOutputSchema,
                                   UserRegisterSchema, UserUpdateSchema, UserInfoOutputSchema)
from src.apps.user.services import (delete_single_user,
                                    get_access_token_schema, get_all_users,
                                    get_single_user, register_user,
                                    update_single_user, get_access_token_schema)
from src.apps.orders.services import get_all_user_orders
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.core.utils import check_field_values
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post(
    "/register", response_model=UserOutputSchema, status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserRegisterSchema, db: Session = Depends(get_db)
) -> UserOutputSchema:
    return register_user(db, user)


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
    response_model=UserInfoOutputSchema,
)
def get_logged_user(
    request_user: User = Depends(authenticate_user),
) -> UserInfoOutputSchema:
    return UserInfoOutputSchema.from_orm(request_user)


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
    response_model=UserOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user)) -> UserOutputSchema:
    check_if_staff(request_user)
    return get_single_user(db, user_id)


@user_router.get(
    "/{user_id}/orders",
    response_model=PagedResponseSchema[OrderOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_user_orders(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[OrderOutputSchema]:
    check_if_staff(request_user)
    return get_all_user_orders(db, user_id, page_params, request.query_params.multi_items())


@user_router.patch(
    "/{user_id}",
    response_model=UserOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_user(
    user_id: int,
    user: UserUpdateSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> UserOutputSchema:
    check_if_staff_or_owner(request_user, "id", user_id)
    return update_single_user(db, user, user_id)


@user_router.post(
    "/change-email",
    status_code=status.HTTP_200_OK
)
def change_email(
    email_update_schema: EmailUpdateSchema, background_tasks: BackgroundTasks, request_user: User = Depends(authenticate_user),
    db: Session = Depends(get_db), auth_jwt: AuthJWT = Depends()
) -> JSONResponse:
    check_field_values(
        request_user.email, email_update_schema.email, "Please type your current mail address in the 'email' field!"
    )
    token = auth_jwt.create_access_token(
        subject=email_update_schema.new_email, algorithm="HS256"
    )
    send_confirmation_mail_change_email(
        email_update_schema,
        db,
        token,
        background_tasks,
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Email change confirmation mail has been sent to the new email address!"}
    )


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    check_if_staff(request_user)
    delete_single_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
