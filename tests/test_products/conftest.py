import pytest
from sqlalchemy.orm import Session

from src.apps.products.schemas import CategoryInputSchema
from src.apps.products.services.category_services import create_category
from tests.test_users.conftest import get_token_header, db_users

list_of_category_input_schemas = [
    CategoryInputSchema(name="drinks"),
    CategoryInputSchema(name="vegetables"),
    CategoryInputSchema(name="furniture")
]

create_category_data = {
    "name": "cars"
}

update_category_data = {
    "name": "fruits"
}


@pytest.fixture(scope="package", autouse=True)
def db_categories(sync_session: Session):
    return ([create_category(sync_session, category) for category in list_of_category_input_schemas])

@pytest.fixture(scope="module")
def post_category() -> dict[str, str]:
    return create_category_data

@pytest.fixture(scope="module")
def update_category() -> dict[str, str]:
    return update_category_data

