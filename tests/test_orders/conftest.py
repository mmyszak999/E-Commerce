import pytest
import copy
from sqlalchemy.orm import Session

from src.apps.orders.schemas import OrderInputSchema, OrderOutputSchema
from src.apps.orders.services import create_order, delete_all_orders, get_single_order
from tests.test_users.conftest import access_token, db_user
from tests.test_products.conftest import db_products, db_categories

from src.core.pagination.models import PageParams
from src.core.factories import OrderFactory

DB_ORDER_SCHEMAS = [OrderFactory.build() for _ in range(3)]

EXISTING_ORDER_DATA = DB_ORDER_SCHEMAS[0]

@pytest.fixture
def db_orders(sync_session: Session, db_products, db_user):
    for order in DB_ORDER_SCHEMAS:
        order.product_ids = [db_products[DB_ORDER_SCHEMAS.index(order)].id]
        order.user_id = db_user.id
    
    return [create_order(sync_session, order) for order in DB_ORDER_SCHEMAS]
