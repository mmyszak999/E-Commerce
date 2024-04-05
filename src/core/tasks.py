from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session

from src.settings.db_settings import settings
from src.apps.orders.services.cart_items_services import delete_invalid_cart_items
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from src.apps.user.models import User
from src.apps.products.routers.category_routers import category_router


def _delete_invalid_cart_items():
    print("oh")
    delete_invalid_cart_items(next(get_db()))


scheduler = BackgroundScheduler()
scheduler.add_job(_delete_invalid_cart_items, 'interval', seconds=10)
scheduler.start()