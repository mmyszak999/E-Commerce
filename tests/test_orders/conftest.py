import pytest
import copy
from sqlalchemy.orm import Session

from src.apps.orders.schemas import OrderInputSchema, OrderOutputSchema
from src.apps.orders.services import create_order, delete_all_orders, get_single_order
from tests.test_users.conftest import get_token_header, db_users
from tests.test_products.conftest import db_products, db_categories

from src.core.pagination.models import PageParams

LIST_OF_ORDER_INPUT_SCHEMAS = [
    OrderInputSchema(),
    OrderInputSchema(),
    OrderInputSchema()
]

CREATE_ORDER_DATA = {
}

UPDATE_ORDER_DATA = {
}

EXISTING_ORDER_DATA = LIST_OF_ORDER_INPUT_SCHEMAS[0]


@pytest.fixture
def db_orders(sync_session: Session, db_products, db_users):
    delete_all_orders(sync_session)
    for order in LIST_OF_ORDER_INPUT_SCHEMAS:
        order.product_ids = [db_products[LIST_OF_ORDER_INPUT_SCHEMAS.index(order)].id]
        order.user_id = db_users[LIST_OF_ORDER_INPUT_SCHEMAS.index(order)].id
    
    return [create_order(sync_session, order) for order in LIST_OF_ORDER_INPUT_SCHEMAS]
    
@pytest.fixture
def post_order(db_products, db_users) -> dict[str, str]:
    CREATE_ORDER_DATA['product_ids'] = [db_products[1].id, db_products[2].id]
    CREATE_ORDER_DATA['user_id'] = db_users[0].id
    return CREATE_ORDER_DATA

@pytest.fixture
def update_order(db_products) -> dict[str, str]:
    UPDATE_ORDER_DATA['product_ids'] = [db_products[0].id]
    return UPDATE_ORDER_DATA

@pytest.fixture
def create_existing_order_data() -> OrderInputSchema:
    return EXISTING_PRODUCT_DATA