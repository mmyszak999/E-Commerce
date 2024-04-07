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

def test_authenticated_user_cannot_get_all_orders(
    sync_client: TestClient,
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get("orders/all", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_anonymous_user_cannot_get_all_orders(
    sync_client: TestClient,
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get("orders/all")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticated_user_can_get_their_orders(
    sync_client: TestClient,
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get("orders/", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert [order["user_id"] for order in response.json()["results"]][0] == db_user.id


def test_anonymous_user_cannot_get_their_orders(
    sync_client: TestClient,
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get("orders/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_user_can_get_single_order(
    sync_client: TestClient,
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get(f"orders/{db_orders[0].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_orders[0].id

def test_authenticated_user_cannot_get_not_their_order(
    sync_client: TestClient,
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get(f"orders/{db_orders[1].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    
def test_anonymous_user_cannot_get_single_order(
    sync_client: TestClient,
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get(f"orders/{db_orders[1].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_staff_user_can_cancel_single_order(
    sync_client: TestClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.patch(f"orders/{db_orders[0].id}/cancel", headers=staff_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    response = sync_client.get(f"orders/{db_orders[0].id}", headers=staff_auth_headers)
    assert response.json()["cancelled"] == True


def test_authenticated_user_cannot_cancel_single_order(
    sync_client: TestClient,
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.patch(f"orders/{db_orders[0].id}/cancel", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_cancel_single_order(
    sync_client: TestClient,
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.patch(f"orders/{db_orders[0].id}/cancel")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    
