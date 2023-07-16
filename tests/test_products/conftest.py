import pytest
from sqlalchemy.orm import Session

from src.apps.products.services.category_services import create_category
from src.apps.products.services.product_services import create_product
from src.core.factories import (CategoryInputSchemaFactory,
                                ProductInputSchemaFactory)
from tests.test_users.conftest import auth_headers, db_user

DB_CATEGORY_SCHEMAS = [CategoryInputSchemaFactory.build() for _ in range(3)]

EXISTING_CATEGORY_DATA = DB_CATEGORY_SCHEMAS[0]

DB_PRODUCT_SCHEMAS = [ProductInputSchemaFactory.build() for _ in range(3)]

EXISTING_PRODUCT_DATA = DB_PRODUCT_SCHEMAS[0]


@pytest.fixture
def db_categories(sync_session: Session):
    return [create_category(sync_session, category) for category in DB_CATEGORY_SCHEMAS]


@pytest.fixture
def db_products(sync_session: Session, db_categories):
    for product in DB_PRODUCT_SCHEMAS:
        category_id = db_categories[
            DB_PRODUCT_SCHEMAS.index(product)
        ].id  # gets a category with the same id as the schema list index
        product.category_ids = [
            category_id
        ]  # assign the category to the product input schema, one category per product as default
    return [create_product(sync_session, product) for product in DB_PRODUCT_SCHEMAS]
