from pydantic import BaseSettings

class DatabaseSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_DATABASE: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int

    class Config:
        env_file = ".env"

    @property
    def postgres_url(self) -> str:
        DATABASE_URL = f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}'
        return DATABASE_URL

settings = DatabaseSettings()