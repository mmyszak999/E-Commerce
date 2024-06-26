from datetime import datetime, timedelta
from typing import Any

import pytest
from freezegun import freeze_time
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from fastapi import BackgroundTasks

from src.apps.orders.schemas import (
    CartItemOutputSchema,
    CartOutputSchema,
    OrderOutputSchema,
)
from src.apps.orders.models import Order
from src.apps.orders.services.cart_services import create_cart, get_single_cart
from src.apps.orders.services.order_services import (
    cancel_orders_with_exceeded_payment_deadline,
    cancel_single_order,
    create_order,
    get_all_orders,
    get_all_user_orders,
    get_single_order,
    fulfill_order,
)
from src.apps.payments.schemas import PaymentOutputSchema
from src.apps.products.schemas import ProductOutputSchema
from src.apps.products.services.product_services import get_single_product_or_inventory
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    ActiveCartException,
    AlreadyExists,
    DoesNotExist,
    EmptyCartException,
    IsOccupied,
    OrderAlreadyCancelledException,
    OrderCancelledException,
    PaymentAlreadyAccepted,
)
from src.core.factories import CartInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_orders.conftest import db_cart_items, db_carts
from tests.test_products.conftest import db_products
from tests.test_users.conftest import db_user
from tests.test_payments.conftest import db_payments, stripe_session, payment_intent


def test_raise_exception_when_order_created_with_nonexistent_user_id(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    with pytest.raises(DoesNotExist):
        create_order(
            sync_session, generate_uuid(), db_carts.results[0].id, BackgroundTasks()
        )


def test_raise_exception_when_order_created_with_nonexistent_cart_id(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(DoesNotExist):
        create_order(sync_session, db_user.id, generate_uuid(), BackgroundTasks())


def test_raise_exception_when_cart_has_no_items_inside(
    sync_session: Session, db_user: UserOutputSchema
):
    cart = create_cart(sync_session, db_user.id)
    with pytest.raises(EmptyCartException):
        create_order(sync_session, db_user.id, cart.id, BackgroundTasks())


def test_if_cart_data_is_managed_correctly_when_creating_order(
    sync_session: Session,
    db_user: UserOutputSchema,
    db_carts: PagedResponseSchema[CartOutputSchema],
):
    cart = db_carts.results[0]
    cart_total_price = cart.cart_total_price
    order = create_order(sync_session, db_user.id, cart.id, BackgroundTasks())

    assert cart_total_price == order.total_order_price

    with pytest.raises(DoesNotExist):
        get_single_cart(sync_session, cart.id)


def test_if_only_one_order_was_returned(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    db_staff_user: UserOutputSchema,
):
    order = get_single_order(sync_session, db_orders.results[1].id)
    assert order.id == db_orders.results[1].id


def test_raise_exception_while_getting_nonexistent_order(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_order(sync_session, generate_uuid())


def test_check_user_orders_ownership(
    sync_session: Session,
    db_user: UserOutputSchema,
    db_orders: PagedResponseSchema[OrderOutputSchema],
):
    orders = get_all_user_orders(sync_session, db_user.id, PageParams(page=1, size=25))

    assert [user_id for user_id in {order.user_id for order in orders.results}][
        0
    ] == db_user.id


def test_if_multiple_orders_were_returned(
    sync_session: Session, db_orders: PagedResponseSchema[OrderOutputSchema]
):
    orders = get_all_orders(sync_session, PageParams(page=1, size=5))
    assert orders.total == db_orders.total


def test_orders_with_exceeded_payment_deadline_will_be_cancelled(
    sync_session: Session, db_orders: PagedResponseSchema[OrderOutputSchema]
):
    """
    the default deadline is 1 hour since order was created
    """
    orders = get_all_orders(sync_session, PageParams())
    cancel_orders_with_exceeded_payment_deadline(sync_session)
    assert len([order for order in orders.results if order.cancelled]) == 0

    with freeze_time(str(datetime.now() + timedelta(minutes=30))):
        cancel_orders_with_exceeded_payment_deadline(sync_session)
        orders = get_all_orders(sync_session, PageParams())
        assert len([order for order in orders.results if order.cancelled]) == 0

    with freeze_time(str(datetime.now() + timedelta(minutes=60))):
        cancel_orders_with_exceeded_payment_deadline(sync_session)
        orders = get_all_orders(sync_session, PageParams())
        assert (
            len(
                [
                    order
                    for order in orders.results
                    if (order.cancelled == True and order.waiting_for_payment == False)
                ]
            )
            == db_orders.total
        )


def test_cancelled_order_cannot_be_cancelled_second_time(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    db_user: UserOutputSchema,
):
    cancel_single_order(sync_session, db_orders.results[0].id)
    with pytest.raises(OrderAlreadyCancelledException):
        cancel_single_order(sync_session, db_orders.results[0].id)


def test_raise_exception_while_cancelling_nonexistent_order(
    sync_session: Session, db_orders: PagedResponseSchema[OrderOutputSchema]
):
    with pytest.raises(DoesNotExist):
        cancel_single_order(sync_session, generate_uuid())


def test_product_quantity_will_be_managed_correctly_when_order_is_being_cancelled(
    sync_session: Session, db_orders: PagedResponseSchema[OrderOutputSchema]
):
    order = db_orders.results[0]
    product = order.order_items[0].product
    order_item_quantity = order.order_items[0].quantity
    product_quantity_for_cart_items = product.inventory.quantity_for_cart_items

    cancel_single_order(sync_session, db_orders.results[0].id)
    product = get_single_product_or_inventory(sync_session, product.id)

    assert (
        product_quantity_for_cart_items + order_item_quantity
        == product.inventory.quantity_for_cart_items
    )


def test_order_statuses_are_managed_correctly_when_payment_accepted(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    stripe_session: dict[str, Any],
    payment_intent: dict[str, Any],
):
    order = db_orders.results[0]
    payment = fulfill_order(
        sync_session,
        stripe_session,
        payment_intent,
        BackgroundTasks(),
        order.id,
        order.total_order_price,
        testing=True,
    )

    assert payment.order.waiting_for_payment == False
    assert payment.order.order_accepted == True
    assert payment.order.payment_accepted == True


def test_product_quantities_are_managed_correctly_when_payment_accepted(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    stripe_session: dict[str, Any],
    payment_intent: dict[str, Any],
):
    order = db_orders.results[0]
    order_item = order.order_items[0]
    order_item_quantity = order_item.quantity
    product = order_item.product
    product_quantity_before_payment_accepted = product.inventory.quantity
    product_quantity_for_cart_items_before_payment_accepted = (
        product.inventory.quantity_for_cart_items
    )

    fulfill_order(
        sync_session,
        stripe_session,
        payment_intent,
        BackgroundTasks(),
        order.id,
        order.total_order_price,
        testing=True,
    )

    product = get_single_product_or_inventory(sync_session, product.id)

    assert (
        product.inventory.quantity
        == product_quantity_before_payment_accepted - order_item_quantity
    )
    assert (
        product.inventory.quantity_for_cart_items
        == product_quantity_for_cart_items_before_payment_accepted
    )
    assert product.inventory.sold == order_item_quantity


def test_raise_exception_when_fulfilling_cancelled_order(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    stripe_session: dict[str, Any],
    payment_intent: dict[str, Any],
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    statement = (
        update(Order).filter(Order.id == db_orders.results[0].id).values(cancelled=True)
    )

    sync_session.execute(statement)
    sync_session.commit()

    order = get_single_order(sync_session, db_orders.results[0].id)
    with pytest.raises(OrderCancelledException):
        fulfill_order(
            sync_session,
            stripe_session,
            payment_intent,
            BackgroundTasks(),
            order.id,
            order.total_order_price,
            testing=True,
        )


def test_raise_exception_when_fulfilling_paid_order(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    stripe_session: dict[str, Any],
    payment_intent: dict[str, Any],
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    order = db_orders.results[0]

    with pytest.raises(PaymentAlreadyAccepted):
        fulfill_order(
            sync_session,
            stripe_session,
            payment_intent,
            BackgroundTasks(),
            order.id,
            order.total_order_price,
            testing=True,
        )

def test_raise_exception_when_fulfilling_nonexistent_order(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    stripe_session: dict[str, Any],
    payment_intent: dict[str, Any]
):

    with pytest.raises(DoesNotExist):
        fulfill_order(
            sync_session,
            stripe_session,
            payment_intent,
            BackgroundTasks(),
            order_id=generate_uuid(),
            testing=True,
        )
