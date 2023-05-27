import pytest
import copy
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select


from src.apps.products.services.category_services import (
    create_category, get_all_categories, get_single_category,
    update_single_category, delete_all_categories, delete_single_category
)
from src.apps.products.schemas import CategoryOutputSchema, CategoryInputSchema
from src.apps.products.models import Category
from src.core.exceptions import (
    DoesNotExist,
    AlreadyExists,
    IsOccupied,
    AuthException
)
from src.core.pagination.models import PageParams


def test_create_category_that_already_exists(
    sync_session: Session,
    create_existing_category_data: CategoryInputSchema,
    db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(AlreadyExists) as exc:
        create_category(sync_session, create_existing_category_data)


def test_if_only_one_category_was_returned(
    sync_session: Session,
    db_categories: list[CategoryOutputSchema]
):
    category = get_single_category(sync_session, db_categories[1].id)

    assert category.id == db_categories[1].id

def test_raise_exception_while_getting_nonexistent_category(
    sync_session: Session,
    db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        get_single_category(sync_session, len(db_categories)+2)


def test_if_multiple_categories_were_returned(
    sync_session: Session,
    db_categories: list[CategoryOutputSchema]
):
    categories = get_all_categories(sync_session, PageParams(page=1, size=5))
    assert len(categories.results) == len(db_categories)


def test_raise_exception_while_updating_nonexistent_category(
    sync_session: Session,
    update_category: dict[str, Any],
    db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        update_single_category(sync_session, CategoryInputSchema(**update_category), len(db_categories)+2)

def test_if_category_can_have_occupied_name(
    sync_session: Session,
    update_category: dict[str, Any],
    db_categories: list[CategoryOutputSchema]
):
    category_data = copy.copy(update_category)
    category_data['name'] = db_categories[1].name
    with pytest.raises(IsOccupied):
        update_single_category(sync_session, CategoryInputSchema(**category_data), db_categories[0].id)

def test_raise_exception_while_deleting_nonexistent_category(
    sync_session: Session,
    db_categories: list[CategoryOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        delete_single_category(sync_session, len(db_categories)+2)