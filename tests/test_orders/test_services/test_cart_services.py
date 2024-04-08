import pytest
from sqlalchemy.orm import Session

from src.apps.orders.schemas import CartItemOutputSchema, CartOutputSchema
from src.apps.orders.services.cart_services import (
    create_cart,
    delete_single_cart,
    get_all_carts,
    get_all_user_carts,
    get_single_cart,
)
from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    ActiveCartException,
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
)
from src.core.factories import CartInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_orders.conftest import db_cart_items, db_carts
from tests.test_products.conftest import db_products
from tests.test_users.conftest import db_user


def test_raise_exception_when_user_create_more_than_one_cart(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema]
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    with pytest.raises(ActiveCartException):
        create_cart(sync_session, db_user.id)


def test_raise_exception_when_cart_created_with_nonexistent_user_id(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    with pytest.raises(DoesNotExist):
        create_cart(sync_session, generate_uuid())


def test_if_only_one_cart_was_returned(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    cart = get_single_cart(sync_session, db_carts.results[1].id)
    assert cart.id == db_carts.results[1].id


def test_raise_exception_while_getting_nonexistent_cart(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_cart(sync_session, generate_uuid())


def test_check_user_carts_ownership(sync_session: Session, db_user: UserOutputSchema):
    create_cart(sync_session, db_user.id)
    carts = get_all_user_carts(sync_session, db_user.id, PageParams(page=1, size=25))

    assert [user_id for user_id in {cart.user_id for cart in carts.results}][
        0
    ] == db_user.id


def test_if_multiple_carts_were_returned(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    carts = get_all_carts(sync_session, PageParams(page=1, size=5))
    assert carts.total == db_carts.total


def test_raise_exception_while_deleting_nonexistent_cart(
    sync_session: Session, db_carts: PagedResponseSchema[CartOutputSchema]
):
    with pytest.raises(DoesNotExist):
        delete_single_cart(sync_session, generate_uuid())
