import pytest
import copy
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

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
    with pytest.raises(DoesNotExist) as exc:
        get_single_order(sync_session, db_orders[-1].id+2)

def test_if_multiple_orders_were_returned(
    sync_session: Session,
    db_orders: list[OrderOutputSchema]
):
    orders = get_all_orders(sync_session, PageParams(page=1, size=5))
    assert len(orders.results) == len(db_orders)


def test_raise_exception_while_updating_nonexistent_order(
    sync_session: Session,
    update_order: dict[str, Any],
    db_orders: list[OrderOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        update_single_order(sync_session, OrderInputSchema(**update_order), db_orders[-1].id+2)

def test_raise_exception_while_deleting_nonexistent_order(
    sync_session: Session,
    db_orders: list[OrderOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        delete_single_order(sync_session, db_orders[-1].id+2)
