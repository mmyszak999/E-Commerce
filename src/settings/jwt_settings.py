from fastapi_jwt_auth import AuthJWT
from pydantic import BaseSettings


class AuthJWTSettings(BaseSettings):
    authjwt_secret_key: str
    authjwt_token_validity_time: int = 24 * 36000

    class Config:
        env_file = ".env"


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()
