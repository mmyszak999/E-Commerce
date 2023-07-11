from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.orders.schemas import OrderOutputSchema
from src.apps.user.models import User
from src.apps.user.schemas import (UserLoginInputSchema, UserOutputSchema,
                                   UserRegisterSchema, UserUpdateSchema)
from src.apps.user.services import (authenticate, delete_single_user,
                                    get_all_users, get_single_user,
                                    register_user, update_single_user)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema, T
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=UserOutputSchema, status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserRegisterSchema, db: Session = Depends(get_db)
) -> UserOutputSchema:
    db_user = register_user(db, user)
    return db_user


@router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=AccessTokenOutputSchema
)
def login_user(
    user_login_schema: UserLoginInputSchema,
    auth_jwt: AuthJWT = Depends(),
    db: Session = Depends(get_db),
) -> AccessTokenOutputSchema:
    user = authenticate(**user_login_schema.dict(), session=db)
    user_schema = UserOutputSchema.from_orm(user)
    access_token = auth_jwt.create_access_token(
        subject=user_schema.json(), algorithm="HS256"
    )

    return AccessTokenOutputSchema(access_token=access_token)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserOutputSchema)
def get_logged_user(
    request_user: User = Depends(authenticate_user),
) -> UserOutputSchema:
    return UserOutputSchema.from_orm(request_user)

@router.get("/", response_model=PagedResponseSchema[UserOutputSchema], dependencies=[Depends(authenticate_user)], status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db), page_params: PageParams = Depends()) -> PagedResponseSchema[UserOutputSchema]:
    db_users = get_all_users(db, page_params)
    return db_users


@router.get(
    "/{user_id}",
    dependencies=[Depends(authenticate_user)],
    response_model=UserOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserOutputSchema:
    db_user = get_single_user(db, user_id)
    return db_user

@router.get("/{user_id}/orders", dependencies=[Depends(authenticate_user)], response_model=PagedResponseSchema[OrderOutputSchema], status_code=status.HTTP_200_OK)
def get_user_orders(user_id: int, db: Session = Depends(get_db), page_params: PageParams = Depends()) -> PagedResponseSchema[OrderOutputSchema]:
    db_orders = get_all_user_orders(db, user_id, page_params)
    return db_orders

@router.patch("/{user_id}", dependencies=[Depends(authenticate_user)], response_model=UserOutputSchema, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: UserUpdateSchema, db: Session = Depends(get_db)) -> UserOutputSchema:
    db_user = update_single_user(db, user, user_id)
    return db_user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response:
    delete_single_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
