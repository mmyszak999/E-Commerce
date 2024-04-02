from fastapi import FastAPI
from sqlalchemy.orm import Session

from src.settings.db_settings import settings
from main import app

from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every

sessionmaker = FastAPISessionMaker(settings.postgres_url)


def aaa():
    print("wwwwa")


@repeat_every(seconds=10)
def aaa_task() -> None:
    aaa()