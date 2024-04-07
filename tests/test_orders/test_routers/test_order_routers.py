from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.orders.schemas import OrderOutputSchema
from src.apps.user.schemas import UserOutputSchema
from tests.test_orders.conftest import db_carts, db_orders
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)

"""
order creating test is placed in tests.test_orders.test_routers.test_cart_item_routers.py
as this functionality is placed in cart_item_routers (POST: carts/{cart_id}/order)
"""

def test_staff_user_can_get_all_orders(
    sync_client: TestClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get("orders/all", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(db_orders) == response.json()["total"]