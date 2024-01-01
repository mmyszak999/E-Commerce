import pytest
from sqlalchemy.orm import Session

from src.apps.products.schemas import CategoryOutputSchema
from src.apps.products.services.category_services import (
    create_category,
    delete_single_category,
    get_all_categories,
    get_single_category,
    update_single_category,
)
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied
from src.core.factories import CategoryInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import DB_CATEGORY_SCHEMAS


def test_create_category_that_already_exists(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(AlreadyExists):
        create_category(sync_session, DB_CATEGORY_SCHEMAS[0])


def test_if_only_one_category_was_returned(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    category = get_single_category(sync_session, db_categories[1].id)

    assert category.id == db_categories[1].id


def test_raise_exception_while_getting_nonexistent_category(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_category(sync_session, generate_uuid())


def test_if_multiple_categories_were_returned(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    categories = get_all_categories(sync_session, PageParams(page=1, size=5))
    assert categories.total == len(db_categories)


def test_raise_exception_while_updating_nonexistent_category(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    update_data = CategoryInputSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        update_single_category(sync_session, update_data, generate_uuid())


def test_if_category_can_have_occupied_name(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    category_data = CategoryInputSchemaFactory().generate(
        name=DB_CATEGORY_SCHEMAS[0].name
    )
    with pytest.raises(IsOccupied):
        update_single_category(sync_session, category_data, db_categories[1].id)


def test_raise_exception_while_deleting_nonexistent_category(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist):
        delete_single_category(sync_session, generate_uuid())
