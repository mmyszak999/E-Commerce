import json

from fastapi import Depends, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.user.models import User
from src.apps.user.exceptions import auth_exception
from src.settings.jwt_settings import AuthJWTSettings
from src.dependencies.get_db import get_db


def authenticate_user(auth_jwt: AuthJWT = Depends(), session: Session = Depends(get_db)) -> User:
    auth_jwt.jwt_required()
    user = json.loads(auth_jwt.get_jwt_subject())
    statement = select(User).filter(User.id==user["id"])
    user = session.scalar(statement)

    if user is None:
        raise auth_exception

    return user


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()