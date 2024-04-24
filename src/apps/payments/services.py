import datetime
from typing import Union, Any

import stripe
from pydantic import BaseSettings
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload

from src.apps.payments.schemas import StripePublishableKeySchema, StripeSessionSchema
from src.apps.orders.models import Order
from src.core.exceptions import (
    DoesNotExist,
    EmptyCartException,
    OrderAlreadyCancelledException,
    PaymentAlreadyAccepted
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists
from src.settings.stripe import settings as stripe_settings



def get_publishable_key() -> StripePublishableKeySchema:
    return StripePublishableKeySchema(publishable_key=str(
        stripe_settings.STRIPE_PUBLISHABLE_KEY)
    )


def create_checkout_session(
    price_data: dict[str, Any], order_id: str,
    settings: BaseSettings=stripe_settings
):
    checkout_session = stripe.checkout.Session.create(
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
            payment_method_types=["card"],
            mode="payment",
            line_items=[price_data],
            metadata={"order_id": order_id},
        )

def get_stripe_session_data(session: Session, order_id: str):
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, "id", order_id)
    
    if order_object.payment_accepted:
        raise PaymentAlreadyAccepted
    
    price_data = {
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"Order #{order_object.id}",
                },
                "unit_amount": int(order_object.total_order_price * 100),
            },
            "quantity": 1,
        }

    stripe_checkout_session = create_checkout_session(
        price_data, order_object.id
    )
    
    return StripeSessionSchema(
        session_id=stripe_checkout_session["id"],
        url=stripe_checkout_session["url"]
    )