from pydantic import BaseSettings

class AuthJWTSettings(BaseSettings):
    authjwt_secret_key: str
    authjwt_token_validity_time: int = 24 * 3600

    class Config:
        env_file = ".env"