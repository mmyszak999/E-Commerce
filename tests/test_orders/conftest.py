import pytest
from sqlalchemy.orm import Session

from src.apps.orders.services.cart_services import create_cart
from src.apps.orders.models import Cart
from src.apps.orders.schemas import CartOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.pagination.models import PageParams
from src.core.utils.utils import if_exists
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)


@pytest.fixture
def db_carts(sync_session: Session, db_user: UserOutputSchema, db_staff_user: UserOutputSchema) -> list[CartOutputSchema]:
    return [create_cart(sync_session, user_id) for user_id in [db_user.id, db_staff_user.id]]
