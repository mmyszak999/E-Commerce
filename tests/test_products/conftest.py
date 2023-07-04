import pytest
import copy
from sqlalchemy.orm import Session

from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema
from src.apps.products.services.category_services import create_category, delete_all_categories, get_single_category
from src.apps.products.services.product_services import create_product, delete_all_products
from tests.test_users.conftest import auth_headers, db_user
from src.core.pagination.models import PageParams
from src.core.factories import CategoryFactory, ProductFactory

DB_CATEGORY_SCHEMAS = [CategoryFactory.build() for _ in range(3)]

EXISTING_CATEGORY_DATA = DB_CATEGORY_SCHEMAS[0]

DB_PRODUCT_SCHEMAS = [ProductFactory.build() for category in range(3)]

EXISTING_PRODUCT_DATA = DB_PRODUCT_SCHEMAS[0]

@pytest.fixture
def db_categories(sync_session: Session):
    return ([create_category(sync_session, category) for category in DB_CATEGORY_SCHEMAS])

@pytest.fixture
def db_products(sync_session: Session, db_categories):
    for product in DB_PRODUCT_SCHEMAS:
        category_id = db_categories[DB_PRODUCT_SCHEMAS.index(product)].id
        product.category_ids = [category_id]
    return [create_product(sync_session, product) for product in DB_PRODUCT_SCHEMAS]
