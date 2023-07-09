from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    TEST_POSTGRES_DB: str

    class Config:
        env_file = ".env"

    @property
    def postgres_url(self) -> str:
        DATABASE_URL = (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        return DATABASE_URL

    @property
    def test_postgres_url(self) -> str:
        TEST_DATABASE_URL = (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.TEST_POSTGRES_DB}"
        )
        return TEST_DATABASE_URL


settings = DatabaseSettings()
