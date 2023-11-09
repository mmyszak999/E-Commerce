from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.user.models import User
from src.core.exceptions import AuthenticationException
from src.dependencies.get_db import get_db
from src.settings.jwt_settings import AuthJWTSettings


def authenticate_user(
    auth_jwt: AuthJWT = Depends(), session: Session = Depends(get_db)
) -> User:
    auth_jwt.jwt_required()
    jwt_subject = auth_jwt.get_jwt_subject()
    user = session.scalar(select(User).filter(User.email == jwt_subject).limit(1))
    if not user:
        raise AuthenticationException("Cannot find user")

    return user


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()
