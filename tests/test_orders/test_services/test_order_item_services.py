from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session
from freezegun import freeze_time

from src.apps.orders.schemas import CartItemOutputSchema, CartOutputSchema, OrderOutputSchema
from src.apps.orders.services.cart_services import create_cart, get_single_cart
from src.apps.orders.services.order_services import (
    create_order,
    get_single_order,
    get_all_orders,
    get_all_user_orders,
)
from src.apps.orders.services.order_items_services import (
    create_order_items,
    get_all_order_items,
    get_all_order_items_for_single_order,
    get_single_order_item
)
from src.apps.products.schemas import ProductOutputSchema
from src.apps.products.services.product_services import (
    get_single_product_or_inventory
)
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    ActiveCartException,
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    EmptyCartException,
    OrderAlreadyCancelled
)
from src.core.factories import CartInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_orders.conftest import db_cart_items, db_carts, db_orders, db_order_items
from tests.test_products.conftest import db_products
from tests.test_users.conftest import db_user


def test_raise_exception_when_cart_has_no_items_when_creating_order_items(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserO
):
    
    with pytest.raises(DoesNotExist):
        create_cart_item(sync_session, cart_item_input, cart_id=generate_uuid())