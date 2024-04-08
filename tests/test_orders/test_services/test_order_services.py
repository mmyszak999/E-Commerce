import pytest
from sqlalchemy.orm import Session

from src.apps.orders.schemas import CartItemOutputSchema, CartOutputSchema, OrderOutputSchema
from src.apps.orders.services.cart_services import create_cart, get_single_cart
from src.apps.orders.services.order_services import (
    create_order,
    get_single_order,
    get_all_orders,
    get_all_user_orders,
    cancel_orders_with_exceeded_payment_deadline,
    cancel_single_order
)
from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    ActiveCartException,
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    EmptyCartException
)
from src.core.factories import CartInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_orders.conftest import db_cart_items, db_carts
from tests.test_products.conftest import db_products
from tests.test_users.conftest import db_user


def test_raise_exception_when_order_created_with_nonexistent_user_id(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    with pytest.raises(DoesNotExist):
        create_order(sync_session, generate_uuid(), db_carts.results[0].id)


def test_raise_exception_when_order_created_with_nonexistent_cart_id(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(DoesNotExist):
        create_order(sync_session, db_user.id, generate_uuid())


def test_raise_exception_when_cart_has_no_items_inside(
    sync_session: Session, db_user: UserOutputSchema
):
    cart = create_cart(sync_session, db_user.id)
    with pytest.raises(EmptyCartException):
        create_order(sync_session, db_user.id, cart.id)


def test_if_cart_data_is_managed_correctly_when_creating_order(
    sync_session: Session, db_user: UserOutputSchema,
    db_carts: PagedResponseSchema[CartOutputSchema]
):
    cart = db_carts.results[0]
    cart_total_price = cart.cart_total_price
    order = create_order(sync_session, db_user.id, cart.id)
    
    assert cart_total_price == order.total_order_price
    
    with pytest.raises(DoesNotExist):
        get_single_cart(sync_session, cart.id)


def test_if_only_one_order_was_returned(
    sync_session: Session, db_orders: PagedResponseSchema[OrderOutputSchema],
    db_staff_user: UserOutputSchema
):
    order = get_single_order(sync_session, db_orders.results[1].id)
    assert order.id == db_orders.results[1].id


def test_raise_exception_while_getting_nonexistent_order(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_order(sync_session, generate_uuid())


def test_check_user_orders_ownership(
    sync_session: Session, db_user: UserOutputSchema,
    db_orders: PagedResponseSchema[OrderOutputSchema]
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
