import pytest
from sqlalchemy.orm import Session

from src.apps.orders.services import create_order
from src.core.factories import OrderInputSchemaFactory
from tests.test_products.conftest import db_categories, db_products
from tests.test_users.conftest import auth_headers, db_user

DB_ORDER_SCHEMAS = [OrderInputSchemaFactory.build() for _ in range(3)]

EXISTING_ORDER_DATA = DB_ORDER_SCHEMAS[0]


@pytest.fixture
def db_orders(sync_session: Session, db_products, db_user):
    for order in DB_ORDER_SCHEMAS:
        order.product_ids = [db_products[DB_ORDER_SCHEMAS.index(order)].id]
        order.user_id = db_user.id

    return [create_order(sync_session, order) for order in DB_ORDER_SCHEMAS]
