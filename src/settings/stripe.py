from pydantic import BaseSettings


class StripeSettings(BaseSettings):
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"


settings = StripeSettings()
