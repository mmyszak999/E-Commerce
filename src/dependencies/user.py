import json

from fastapi import Depends, status
from fastapi_jwt_auth import AuthJWT

from src.apps.user.models.user import User
from src.apps.user.exceptions import AuthException
from src.settings.jwt_settings import AuthJWTSettings


def authenticate_user(auth_jwt: AuthJWT = Depends()) -> User:
    auth_jwt.jwt_required()
    user = json.loads(auth_jwt.get_jwt_subject())
    user = User.filter(id=user["id"]).first()

    if user is None:
        raise AuthException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
            )

    return user


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()