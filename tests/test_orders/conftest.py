import pytest
from sqlalchemy.orm import Session

from src.apps.orders.services.cart_services import create_cart, get_all_carts
from src.apps.orders.services.cart_items_services import create_cart_item, get_all_cart_items
from src.apps.orders.models import Cart
from src.apps.orders.schemas import CartOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.factories import CartItemInputSchemaFactory, CartInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.utils.utils import if_exists
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)

from tests.test_products.conftest import db_products, db_categories

DB_CART_ITEMS_SCHEMAS = [CartItemInputSchemaFactory().generate(product_id="") for _ in range(3)]


@pytest.fixture
def db_carts(
    sync_session: Session, db_user: UserOutputSchema, db_staff_user: UserOutputSchema,
    db_categories, db_products
) -> list[CartOutputSchema]:
    created_carts = [create_cart(sync_session, user.id) for user in [db_user, db_staff_user]]
    [setattr(cart_item_schema, "product_id", product.id)
        for cart_item_schema, product in zip(DB_CART_ITEMS_SCHEMAS, db_products)]
    [create_cart_item(sync_session, cart_item_schema, cart_id) for cart_item_schema, cart_id
        in zip(DB_CART_ITEMS_SCHEMAS, [created_carts[0].id, created_carts[1].id, created_carts[0].id])]
    return get_all_carts(sync_session, PageParams())
    

@pytest.fixture
def db_cart_items(sync_session: Session):
    return get_all_cart_items(sync_session, PageParams())