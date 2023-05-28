import pytest
from sqlalchemy.orm import Session

from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema
from src.apps.products.services.category_services import create_category, delete_all_categories, get_all_categories
from src.apps.products.services.product_services import create_product, delete_all_products
from tests.test_users.conftest import get_token_header, db_users

from src.core.pagination.models import PageParams

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

LIST_OF_PRODUCT_INPUT_SCHEMAS = [
    ProductInputSchema(name="sprite", price=4.99),
    ProductInputSchema(name='avocado', price=8.99),
    ProductInputSchema(name='wardrobe', price=799.99)
]


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

@pytest.fixture
def db_products(sync_session: Session, db_categories):
    delete_all_products(sync_session)
    for product in LIST_OF_PRODUCT_INPUT_SCHEMAS:
        category_id = db_categories[LIST_OF_PRODUCT_INPUT_SCHEMAS.index(product)].id
        product.categories_ids.append(category_id)
    
    return [create_product(sync_session, product) for product in LIST_OF_PRODUCT_INPUT_SCHEMAS]
    
