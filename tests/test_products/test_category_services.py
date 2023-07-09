import copy
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.products.models import Category
from src.apps.products.schemas import CategoryInputSchema, CategoryOutputSchema
from src.apps.products.services.category_services import (
    create_category, delete_all_categories, delete_single_category,
    get_all_categories, get_single_category, update_single_category)
from src.core.exceptions import (AlreadyExists, AuthException, DoesNotExist,
                                 IsOccupied)
from src.core.factories import CategoryInputSchemaFactory
from src.core.pagination.models import PageParams
from tests.test_products.conftest import DB_CATEGORY_SCHEMAS


def test_create_category_that_already_exists(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(AlreadyExists) as exc:
        create_category(sync_session, DB_CATEGORY_SCHEMAS[0])


def test_if_only_one_category_was_returned(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    category = get_single_category(sync_session, db_categories[1].id)

    assert category.id == db_categories[1].id


def test_raise_exception_while_getting_nonexistent_category(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        get_single_category(sync_session, len(db_categories) + 2)


def test_if_multiple_categories_were_returned(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    categories = get_all_categories(sync_session, PageParams(page=1, size=5))
    assert categories.total == len(db_categories)


def test_raise_exception_while_updating_nonexistent_category(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    update_data = CategoryInputSchemaFactory.build()
    with pytest.raises(DoesNotExist) as exc:
        update_single_category(sync_session, update_data, len(db_categories) + 2)


def test_if_category_can_have_occupied_name(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    category_data = CategoryInputSchemaFactory.build(name=DB_CATEGORY_SCHEMAS[0].name)
    with pytest.raises(IsOccupied):
        update_single_category(sync_session, category_data, db_categories[1].id)


def test_raise_exception_while_deleting_nonexistent_category(
    sync_session: Session, db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        delete_single_category(sync_session, len(db_categories) + 2)
