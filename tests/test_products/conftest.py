import pytest
from sqlalchemy.orm import Session

from src.apps.products.schemas import CategoryInputSchema
from src.apps.products.services.category_services import create_category, delete_all_categories
from tests.test_users.conftest import get_token_header, db_users

LIST_OF_CATEGORY_INPUT_SCHEMAS = [
    CategoryInputSchema(name="drinks"),
    CategoryInputSchema(name="vegetables"),
    CategoryInputSchema(name="furniture")
]

CREATE_CATEGORY_DATA = {
    "name": "cars"
}

UPDATE_CATEGORY_DATA = {
    "name": "fruits"
}

EXISTING_CATEGORY_DATA = LIST_OF_CATEGORY_INPUT_SCHEMAS[0]


@pytest.fixture
def db_categories(sync_session: Session):
    delete_all_categories(sync_session)
    return ([create_category(sync_session, category) for category in LIST_OF_CATEGORY_INPUT_SCHEMAS])

@pytest.fixture
def post_category() -> dict[str, str]:
    return CREATE_CATEGORY_DATA

@pytest.fixture
def update_category() -> dict[str, str]:
    return UPDATE_CATEGORY_DATA

@pytest.fixture
def create_existing_category_data() -> CategoryInputSchema:
    return EXISTING_CATEGORY_DATA


