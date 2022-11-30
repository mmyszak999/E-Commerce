from typing import Union

from fastapi import Depends, HTTPException, status, Response
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.user.schemas.user import (
    UserUpdateSchema,
    UserOutputSchema,
    UserRegisterSchema,
    UserLoginInputSchema
)
from src.apps.user.services.user import (
    register_user,
    get_single_user,
    get_all_users,
    delete_single_user,
    update_single_user,
    authenticate
)
from src.apps.user.utils.get_db import get_db
from src.utils.jwt import AccessTokenOutputSchema
from src.settings.jwt_settings import AuthJWTSettings

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOutputSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserRegisterSchema, db :Session = Depends(get_db)) -> UserOutputSchema:
    db_user = register_user(db, user)
    return db_user


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()

@router.post("/login", status_code=status.HTTP_200_OK, response_model=AccessTokenOutputSchema)
def login_user(user_login_schema: UserLoginInputSchema, auth_jwt: AuthJWT = Depends(), db :Session = Depends(get_db)) -> AccessTokenOutputSchema:
    user = authenticate(db, **user_login_schema.dict())
    user_schema = UserOutputSchema.from_orm(user)
    access_token = auth_jwt.create_access_token(subject=user_schema.json(), algorithm="HS256")

    return AccessTokenOutputSchema(access_token=access_token)


@router.get("/", response_model=list[UserOutputSchema], status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)) -> list[UserOutputSchema]:
    db_users = get_all_users(db)
    return db_users

@router.get("/{user_id}", response_model=UserOutputSchema, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserOutputSchema:
    db_user = get_single_user(db, user_id)
    return db_user

@router.put("/{user_id}", response_model=UserOutputSchema, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: UserUpdateSchema, db: Session = Depends(get_db)) -> UserOutputSchema:
    db_user = update_single_user(db, user, user_id)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response:
    delete_single_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)