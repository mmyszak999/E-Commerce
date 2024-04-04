from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session

from src.settings.db_settings import settings
from src.apps.products.services.category_services import delete_single_category
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from src.apps.user.models import User
from src.apps.products.routers.category_routers import category_router


def job_function():
    print("here")
    """delete_single_category(
        next(get_db()), "bca888b8-f8f0-4f72-aab8-9b21cd262dcc"
        )"""


scheduler = BackgroundScheduler()
scheduler.add_job(job_function, 'interval', seconds=5)
scheduler.start()