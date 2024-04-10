from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from sqlalchemy.orm import Session

from src.apps.orders.schemas import (
    CartItemOutputSchema,
    CartOutputSchema,
    OrderItemOutputSchema,
    OrderOutputSchema,
)
from src.apps.orders.services.cart_services import create_cart, get_single_cart
from src.apps.orders.services.order_items_services import (
    create_order_items,
    get_all_order_items,
    get_all_order_items_for_single_order,
    get_single_order_item,
)
from src.apps.orders.services.order_services import (
    create_order,
    get_all_orders,
    get_all_user_orders,
    get_single_order,
)
from src.apps.products.schemas import ProductOutputSchema
from src.apps.products.services.product_services import get_single_product_or_inventory
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    ActiveCartException,
    AlreadyExists,
    DoesNotExist,
    EmptyCartException,
    IsOccupied,
    OrderAlreadyCancelled,
)
from src.core.factories import CartInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_orders.conftest import (
    db_cart_items,
    db_carts,
    db_order_items,
    db_orders,
)
from tests.test_products.conftest import db_products
from tests.test_users.conftest import db_user


def test_if_only_one_order_item_was_returned(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    db_order_items: PagedResponseSchema[OrderItemOutputSchema],
):
    order_item = get_single_order_item(sync_session, db_order_items.results[1].id)
    assert order_item.id == db_order_items.results[1].id


def test_raise_exception_while_getting_nonexistent_order_item(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    db_order_items: PagedResponseSchema[OrderItemOutputSchema],
):
    with pytest.raises(DoesNotExist):
        get_single_order_item(sync_session, generate_uuid())


def test_all_order_items_in_the_order_belongs_to_the_same_order(
    sync_session: Session,
    db_user: UserOutputSchema,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    db_order_items: PagedResponseSchema[OrderItemOutputSchema],
):
    order_items = get_all_order_items_for_single_order(
        sync_session, db_orders.results[0].id, PageParams(page=1, size=25)
    )
    print(
        [
            order_id
            for order_id in {order_item.order_id for order_item in order_items.results}
        ]
    )
    assert [
        order_id
        for order_id in {order_item.order_id for order_item in order_items.results}
    ][0] == db_orders.results[0].id


def test_if_multiple_order_items_were_returned(
    sync_session: Session,
    db_orders: PagedResponseSchema[OrderOutputSchema],
    db_order_items: PagedResponseSchema[OrderItemOutputSchema],
):
    order_items = get_all_order_items(sync_session, PageParams(page=1, size=5))
    assert order_items.total == db_order_items.total
