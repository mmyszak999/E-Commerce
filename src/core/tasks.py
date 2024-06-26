from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

from src.apps.orders.services.cart_items_services import delete_invalid_cart_items
from src.apps.orders.services.order_services import (
    cancel_orders_with_exceeded_payment_deadline,
)
from src.apps.products.routers.category_routers import category_router
from src.apps.user.models import User
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user
from src.settings.db_settings import settings


def _delete_invalid_cart_items():
    delete_invalid_cart_items(next(get_db()))


def _cancel_orders_with_exceeded_payment_deadline():
    cancel_orders_with_exceeded_payment_deadline(next(get_db()))


scheduler = BackgroundScheduler()
scheduler.add_job(_delete_invalid_cart_items, "interval", seconds=60)
scheduler.add_job(_cancel_orders_with_exceeded_payment_deadline, "interval", seconds=60)
scheduler.start()
