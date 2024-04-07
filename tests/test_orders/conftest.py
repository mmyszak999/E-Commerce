import pytest
from sqlalchemy.orm import Session

from src.apps.orders.models import Cart
from src.apps.orders.schemas import (
    CartOutputSchema, CartItemOutputSchema,
    OrderOutputSchema, OrderItemOutputSchema
)
from src.apps.orders.services.cart_items_services import (
    create_cart_item,
    get_all_cart_items
)
from src.apps.orders.services.cart_services import create_cart, get_all_carts
from src.apps.orders.services.order_services import create_order
from src.apps.user.schemas import UserOutputSchema
from src.apps.products.schemas import CategoryOutputSchema, ProductOutputSchema
from src.core.factories import CartInputSchemaFactory, CartItemInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import if_exists
from tests.test_products.conftest import db_categories, db_products
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)

DB_CART_ITEMS_SCHEMAS = [
    CartItemInputSchemaFactory().generate(product_id="") for _ in range(3)
]


@pytest.fixture
def db_carts(
    sync_session: Session,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
    db_categories: list[CategoryOutputSchema],
    db_products: list[ProductOutputSchema],
) -> PagedResponseSchema[CartOutputSchema]:
    created_carts = [
        create_cart(sync_session, user.id) for user in [db_user, db_staff_user]
    ]
    [
        setattr(cart_item_schema, "product_id", product.id)
        for cart_item_schema, product in zip(DB_CART_ITEMS_SCHEMAS, db_products)
    ]
    [
        create_cart_item(sync_session, cart_item_schema, cart_id)
        for cart_item_schema, cart_id in zip(
            DB_CART_ITEMS_SCHEMAS,
            [created_carts[0].id, created_carts[1].id, created_carts[0].id],
        )
    ]
    return get_all_carts(sync_session, PageParams())


@pytest.fixture
def db_cart_items(sync_session: Session) -> PagedResponseSchema[CartItemOutputSchema]:
    return get_all_cart_items(sync_session, PageParams())


@pytest.fixture
def db_orders(
    sync_session: Session,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
    db_categories: list[CategoryOutputSchema],
    db_products: list[ProductOutputSchema],
    db_carts: PagedResponseSchema[CartOutputSchema]
) -> list[OrderOutputSchema]:
    return [
        create_order(sync_session, user.id, cart.id) for user, cart in zip(
            [db_user, db_staff_user], [db_carts.results[0], db_carts.results[1]])
        ]
