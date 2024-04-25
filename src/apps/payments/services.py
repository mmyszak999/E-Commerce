import datetime
from typing import Union, Any

import stripe
from fastapi import Request
from pydantic import BaseSettings
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload

from src.apps.payments.schemas import (StripePublishableKeySchema, StripeSessionSchema,
                                       UserPaymentOutputSchema, PaymentOutputSchema)
from src.apps.payments.models import Payment
from src.apps.user.models import User
from src.apps.orders.models import Order
from src.core.exceptions import (
    DoesNotExist,
    EmptyCartException,
    OrderAlreadyCancelledException,
    PaymentAlreadyAccepted
)
from src.apps.orders.services.order_services import fulfill_order
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists
from src.settings.stripe import settings as stripe_settings


def get_single_payment(
    session: Session, payment_id: str, as_staff: bool = False
) -> Union[PaymentOutputSchema, UserPaymentOutputSchema]:
    if not (payment_object := if_exists(Payment, "id", payment_id, session)):
        raise DoesNotExist(Payment.__name__, "id", payment_id)

    if as_staff:
        return PaymentOutputSchema.from_orm(payment_object)
    return UserPaymentOutputSchema.from_orm(payment_object)


def get_all_payments(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[PaymentOutputSchema]:
    query = select(Payment)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Payment)

    return paginate(
        query=query,
        response_schema=PaymentOutputSchema,
        table=Payment,
        page_params=page_params,
        session=session,
    )


def get_all_user_payments(
    session: Session,
    user_id: str,
    page_params: PageParams,
    query_params: list[tuple] = None,
) -> PagedResponseSchema[UserPaymentOutputSchema]:
    query = (
        select(Payment).filter(User.id == user_id).join(User, Payment.user_id == User.id)
    )
    if query_params:
        query = filter_and_sort_instances(query_params, query, Payment)

    return paginate(
        query=query,
        response_schema=UserPaymentOutputSchema,
        table=Payment,
        page_params=page_params,
        session=session,
    )


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
    return checkout_session

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

async def handle_stripe_webhook_event(
    session: Session,
    request: Request,
    settings: BaseSettings=stripe_settings
):
    endpoint_secret = settings.WEBHOOK_SECRET
    payload = await request.body()
    sig_header = request.headers["stripe-signature"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as err:
        print(err)
        raise Exception
    except stripe.error.SignatureVerificationError as err:
        print(err)
        raise Exception

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        payment_intent = stripe.PaymentIntent.retrieve(id=session["payment_intent"])
        print("slatt")
        """self.service_class.fullfill_order(
            session=session, payment_intent=payment_intent
        )"""
        fulfill_order()
    return