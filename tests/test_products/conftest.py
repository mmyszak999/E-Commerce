import pytest
from sqlalchemy.orm import Session

from src.apps.products.services.category_services import create_category
from src.apps.products.services.product_services import create_product
from src.core.utils.utils import if_exists
from src.core.factories import CategoryInputSchemaFactory, ProductInputSchemaFactory, InventoryInputSchemaFactory
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)

DB_CATEGORY_SCHEMAS = [CategoryInputSchemaFactory().generate() for _ in range(3)]

DB_INVENTORY_SCHEMAS = [InventoryInputSchemaFactory().generate() for _ in range(3)]

DB_PRODUCT_SCHEMAS = [ProductInputSchemaFactory().generate(inventory=DB_INVENTORY_SCHEMAS[index]) for index in range(3)]


@pytest.fixture
def db_categories(sync_session: Session):
    return [create_category(sync_session, category) for category in DB_CATEGORY_SCHEMAS]


@pytest.fixture
def db_products(sync_session: Session, db_categories):
    for index, product in enumerate(DB_PRODUCT_SCHEMAS):
        category_id = db_categories[
            index
        ].id  # gets a category with the same id as the schema list index
        product.category_ids = [
            category_id
        ]  # assign the category to the product input schema, one category per product as default
    return [create_product(sync_session, product) for product in DB_PRODUCT_SCHEMAS]
