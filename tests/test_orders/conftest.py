import pytest
import copy
from sqlalchemy.orm import Session

from src.apps.orders.schemas import OrderInputSchema, OrderOutputSchema
from src.apps.products.services.category_services import create_category, delete_all_categories, get_single_category
from src.apps.products.services.product_services import create_product, delete_all_products
from tests.test_users.conftest import get_token_header, db_users

from src.core.pagination.models import PageParams