import pytest
import copy
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from src.apps.products.services.product_services import (
   create_product, get_all_products, get_single_product,
   update_single_product, delete_single_product
)
from src.apps.products.schemas import ProductOutputSchema, ProductInputSchema
from src.apps.products.models import Product
from src.core.exceptions import (
    DoesNotExist,
    AlreadyExists,
    IsOccupied,
    AuthException
)
from src.core.pagination.models import PageParams


def test_create_product_that_already_exists(
    sync_session: Session,
    create_existing_product_data: ProductInputSchema,
    db_products: list[ProductOutputSchema]
):
    with pytest.raises(AlreadyExists) as exc:
        create_product(sync_session, create_existing_product_data)


def test_if_only_one_product_was_returned(
    sync_session: Session,
    db_products: list[ProductOutputSchema]
):
    product = get_single_product(sync_session, db_products[1].id)

    assert product.id == db_products[1].id

def test_raise_exception_while_getting_nonexistent_product(
    sync_session: Session,
    db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        get_single_product(sync_session, db_products[-1].id+2)


def test_if_multiple_products_were_returned(
    sync_session: Session,
    db_products: list[ProductOutputSchema]
):
    products = get_all_products(sync_session, PageParams(page=1, size=5))
    assert len(products.results) == len(db_products)


def test_raise_exception_while_updating_nonexistent_product(
    sync_session: Session,
    update_product: dict[str, Any],
    db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        update_single_product(sync_session, ProductInputSchema(**update_product), db_products[-1].id+2)

def test_if_product_can_have_occupied_name(
    sync_session: Session,
    update_product: dict[str, Any],
    db_products: list[ProductOutputSchema]
):
    product_data = copy.copy(update_product)
    product_data['name'] = db_products[1].name
    with pytest.raises(IsOccupied):
        update_single_product(sync_session, ProductInputSchema(**product_data), db_products[0].id)

def test_raise_exception_while_deleting_nonexistent_product(
    sync_session: Session,
    db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        delete_single_product(sync_session, db_products[-1].id+2)
