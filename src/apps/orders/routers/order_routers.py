from typing import Union

import stripe
from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.orders.schemas import OrderOutputSchema, UserOrderOutputSchema
from src.apps.orders.services.order_services import (
    cancel_single_order,
    get_all_orders,
    get_all_user_orders,
    get_single_order,
)
from src.apps.payments.schemas import StripePublishableKeySchema, StripeSessionSchema
from src.apps.payments.services import get_publishable_key, get_stripe_session_data
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user
from src.settings.stripe import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
order_router = APIRouter(prefix="/orders", tags=["order"])


@order_router.get(
    "/all",
    response_model=PagedResponseSchema[OrderOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_orders(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[OrderOutputSchema]:
    check_if_staff(request_user)
    return get_all_orders(db, page_params, request.query_params.multi_items())


@order_router.get(
    "/",
    response_model=PagedResponseSchema[UserOrderOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_logged_user_orders(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserOrderOutputSchema]:
    return get_all_user_orders(
        db, request_user.id, page_params, request.query_params.multi_items()
    )


@order_router.get(
    "/all/{order_id}",
    response_model=OrderOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> OrderOutputSchema:
    db_order = get_single_order(db, order_id)
    check_if_staff(request_user)
    return db_order


@order_router.get(
    "/{order_id}",
    response_model=Union[OrderOutputSchema, UserOrderOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[OrderOutputSchema, UserOrderOutputSchema]:
    db_order = get_single_order(db, order_id)
    if check_if_staff_or_owner(request_user, "id", db_order.user_id):
        if request_user.is_staff:
            return get_single_order(db, order_id, as_staff=True)
        return get_single_order(db, order_id)


@order_router.patch(
    "/{order_id}/cancel",
    status_code=status.HTTP_200_OK,
)
def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    check_if_staff(request_user)
    cancel_single_order(db, order_id, True)
    return {"message": "Order has been cancelled"}


"""
part of the routers related to stripe payment system
"""

@order_router.get(
    "/stripe",
    response_model=StripePublishableKeySchema,
    status_code=status.HTTP_200_OK,
)
def get_stripe_publishable_key() -> StripePublishableKeySchema:
    return get_publishable_key()


@order_router.get(
    "/{order_id}/session",
    response_model=StripeSessionSchema,
    status_code=status.HTTP_200_OK,
)
def get_stripe_session(
    order_id: str,
    db: Session = Depends(get_db),
) -> StripeSessionSchema:
    return get_stripe_session_data(db, order_id)
    
