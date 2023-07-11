import pytest
import copy
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from src.apps.user.schemas import UserOutputSchema
from src.apps.products.schemas import ProductOutputSchema
from src.apps.orders.services import (
   create_order, get_single_order, get_all_orders, get_all_user_orders,
   update_single_order, delete_single_order
)
from src.apps.orders.schemas import OrderInputSchema, OrderOutputSchema
from src.apps.orders.models import Order
from src.core.exceptions import (
    DoesNotExist,
    AlreadyExists,
    IsOccupied,
    AuthException
)
from src.core.pagination.models import PageParams
from src.core.factories import OrderInputSchemaFactory
from tests.test_orders.conftest import DB_ORDER_SCHEMAS

        
def test_if_only_one_order_was_returned(
    sync_session: Session,
    db_orders: list[OrderOutputSchema]
):
    order = get_single_order(sync_session, db_orders[1].id)

    assert order.id == db_orders[1].id

def test_raise_exception_while_getting_nonexistent_order(
    sync_session: Session,
    db_orders: list[OrderOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_order(sync_session, len(db_orders)+2)

def test_if_user_retrieve_only_their_orders(
    sync_session: Session,
    db_orders: list[OrderOutputSchema],
    db_user: UserOutputSchema
):
    user_orders = get_all_user_orders(sync_session, db_user.id, PageParams(page=1, size=5))
    
    assert {order.id for order in user_orders.results} == {order.id for order in db_orders if order.user.id == db_user.id}

def test_if_multiple_orders_were_returned(
    sync_session: Session,
    db_orders: list[OrderOutputSchema]
):
    orders = get_all_orders(sync_session, PageParams(page=1, size=5))
    assert orders.total == len(db_orders)
    
def test_raise_exception_while_updating_nonexistent_order(
    sync_session: Session,
    db_orders: list[OrderOutputSchema]
):
    update_data = OrderInputSchemaFactory.build()
    with pytest.raises(DoesNotExist):
        update_single_order(sync_session, update_data, len(db_orders)+2)

def test_raise_exception_while_deleting_nonexistent_order(
    sync_session: Session,
    db_orders: list[OrderOutputSchema]
):
    with pytest.raises(DoesNotExist):
        delete_single_order(sync_session, len(db_orders)+2)
