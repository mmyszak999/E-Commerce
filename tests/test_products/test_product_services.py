import pytest
from sqlalchemy.orm import Session

from src.apps.products.schemas import ProductOutputSchema
from src.apps.products.services.product_services import (create_product,
                                                         delete_all_products,
                                                         delete_single_product,
                                                         get_single_product,
                                                         update_single_product)
from src.core.exceptions import (AlreadyExists, DoesNotExist,
                                 IsOccupied)
from src.core.factories import ProductInputSchemaFactory
from src.core.pagination.models import PageParams
from tests.test_products.conftest import DB_PRODUCT_SCHEMAS


def test_create_product_that_already_exists(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    with pytest.raises(AlreadyExists):
        create_product(sync_session, DB_PRODUCT_SCHEMAS[0])


def test_if_only_one_product_was_returned(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    product = get_single_product(sync_session, db_products[1].id)

    assert product.id == db_products[1].id


def test_raise_exception_while_getting_nonexistent_product(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_product(sync_session, len(db_products) + 2)


def test_if_multiple_products_were_returned(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    products = get_all_products(sync_session, PageParams(page=1, size=5))
    assert products.total == len(db_products)


def test_raise_exception_while_updating_nonexistent_product(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    update_data = ProductInputSchemaFactory.build()
    with pytest.raises(DoesNotExist):
        update_single_product(sync_session, update_data, len(db_products) + 2)


def test_if_product_can_have_occupied_name(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    product_data = ProductInputSchemaFactory.build(
        name=DB_PRODUCT_SCHEMAS[0].name, category_ids=[]
    )
    with pytest.raises(IsOccupied):
        update_single_product(sync_session, product_data, db_products[1].id)


def test_raise_exception_while_deleting_nonexistent_product(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        delete_single_product(sync_session, len(db_products) + 2)
