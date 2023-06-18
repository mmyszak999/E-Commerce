import json

from fastapi import Depends, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.user.models import User
from src.settings.jwt_settings import AuthJWTSettings
from src.dependencies.get_db import get_db
from src.core.exceptions import AuthException


def authenticate_user(auth_jwt: AuthJWT = Depends(), session: Session = Depends(get_db)) -> User:
    auth_jwt.jwt_required()
    user_subject_id = json.loads(auth_jwt.get_jwt_subject())
    user = session.scalar(select(User).filter(User.id==user_subject_id).limit(1))

    if not user:
        raise AuthException("Cannot find user")

    return user


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()