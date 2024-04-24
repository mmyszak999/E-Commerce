from typing import Union

import stripe
from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session


from src.apps.payments.schemas import (
    StripePublishableKeySchema,
    StripeSessionSchema,
    PaymentOutputSchema,
    UserPaymentOutputSchema
)
from src.apps.payments.services import (
    get_publishable_key,
    get_stripe_session_data,
    handle_stripe_webhook_event,
    get_all_payments,
    get_all_user_payments,
    get_single_payment
)
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user
from src.settings.stripe import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_router = APIRouter(prefix="/stripe", tags=["stripe"])
payment_router = APIRouter(prefix="/payments", tags=["payment"])


@stripe_router.post(
    "/webhook/",
    status_code=status.HTTP_200_OK,
)
async def handle_webhook_event(
    request: Request
) -> None:
    return await handle_stripe_webhook_event(request)

@payment_router.get(
    "/all",
    response_model=PagedResponseSchema[PaymentOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_payments(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[PaymentOutputSchema]:
    check_if_staff(request_user)
    return get_all_payments(db, page_params, request.query_params.multi_items())


@payment_router.get(
    "/",
    response_model=PagedResponseSchema[UserPaymentOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_logged_user_payments(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserPaymentOutputSchema]:
    return get_all_user_payments(
        db, request_user.id, page_params, request.query_params.multi_items()
    )


@payment_router.get(
    "/{payment_id}",
    response_model=Union[PaymentOutputSchema, UserPaymentOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[PaymentOutputSchema, UserPaymentOutputSchema]:
    db_payment = get_single_payment(db, payment_id)
    if check_if_staff_or_owner(request_user, "id", db_payment.user_id):
        if request_user.is_staff:
            return get_single_payment(db, payment_id, as_staff=True)
        return get_single_payment(db, payment_id)

