from typing import Any

import pytest
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from src.apps.orders.schemas import OrderOutputSchema
from src.apps.orders.services.order_services import fulfill_order
from src.apps.payments.models import Payment
from src.apps.payments.schemas import PaymentOutputSchema
from src.apps.payments.services import get_all_payments
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from tests.test_orders.conftest import (
    db_cart_items,
    db_carts,
    db_order_items,
    db_orders,
)
from tests.test_products.conftest import db_categories, db_products
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)

STRIPE_SESSION_DATA = {
    "id": "cs_test_id",
    "object": "checkout.session",
    "metadata": {"order_id": "345fedf34--345435-3452133dwe"},
    "mode": "payment",
    "payment_method_types": ["card"],
    "payment_status": "paid",
}

PAYMENT_INTENT_DATA = {
    "id": "test_payment_intent_id",
    "object": "payment_intent",
    "amount": 1000,
    "latest_charge": "cs_2345erfw34r43r34",
}


@pytest.fixture
def stripe_session() -> dict[str, Any]:
    return STRIPE_SESSION_DATA


@pytest.fixture
def payment_intent() -> dict[str, Any]:
    return PAYMENT_INTENT_DATA


@pytest.fixture
def db_payments(
    sync_session: Session,
    stripe_session: dict[str, Any],
    payment_intent: dict[str, Any],
    db_orders: PagedResponseSchema[OrderOutputSchema],
) -> PagedResponseSchema[PaymentOutputSchema]:
    [
        fulfill_order(
            sync_session,
            stripe_session,
            payment_intent,
            BackgroundTasks(),
            order_id=order.id,
        )
        for order in db_orders.results
    ]
    return get_all_payments(sync_session, PageParams())