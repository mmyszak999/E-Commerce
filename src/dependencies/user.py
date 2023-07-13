import yaml

from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.user.models import User
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import AuthException
from src.dependencies.get_db import get_db
from src.settings.jwt_settings import AuthJWTSettings


def authenticate_user(
    auth_jwt: AuthJWT = Depends(), session: Session = Depends(get_db)
) -> User:
    auth_jwt.jwt_required()
    jwt_subject = auth_jwt.get_jwt_subject()
    user = session.scalar(select(User).filter(User.username == jwt_subject).limit(1))

    if not user:
        raise AuthException("Cannot find user")

    return user

def check_permission(request_user: User) -> None:
    if not request_user.is_superuser:
        raise AuthException("You don't have superuser permission to access the group of resources")


def check_object_permission(user_id: int, request_user: User) -> None:
    if not(request_user.is_superuser or request_user.id == user_id):
        raise AuthException("You don't have permission to access the resource")
    

@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()
