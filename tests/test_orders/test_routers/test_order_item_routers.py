from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.orders.schemas import OrderItemOutputSchema, OrderOutputSchema
from src.apps.user.schemas import UserOutputSchema
from tests.test_orders.conftest import db_carts, db_order_items, db_orders
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


def test_staff_user_can_get_any_single_order_item(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
    db_order_items: list[OrderItemOutputSchema],
    db_staff_user: UserOutputSchema,
):
    response = sync_client.get(
        f"orders/{db_orders.results[1].id}/items/{db_order_items.results[1].id}",
        headers=staff_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["order_id"] == db_orders.results[1].id
    assert response.json()["id"] == db_order_items.results[1].id


def test_authenticated_user_cannot_get_order_item_from_not_their_order(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
    db_order_items: list[OrderItemOutputSchema],
    db_user: UserOutputSchema,
):
    response = sync_client.get(
        f"orders/{db_orders.results[1].id}/items/{db_order_items.results[1].id}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_get_single_order_item(
    sync_client: TestClient,
    db_orders: list[OrderOutputSchema],
    db_order_items: list[OrderItemOutputSchema],
):
    response = sync_client.get(
        f"orders/{db_orders.results[1].id}/items/{db_order_items.results[1].id}"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_staff_user_can_get_order_items_from_any_order(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
    db_order_items: list[OrderItemOutputSchema],
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
):
    order = [order for order in db_orders.results if order.user_id == db_user.id][0]

    response = sync_client.get(f"orders/{order.id}/items/", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(order.order_items)


def test_authenticated_user_can_get_order_items_only_from_their_order(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
    db_order_items: list[OrderItemOutputSchema],
    db_user: UserOutputSchema,
):
    response = sync_client.get(
        f"orders/{db_orders.results[0].id}/items/", headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_orders.results[0].order_items)

    response = sync_client.get(
        f"orders/{db_orders.results[1].id}/items/", headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_get_order_items(
    sync_client: TestClient,
    db_orders: list[OrderOutputSchema],
    db_order_items: list[OrderItemOutputSchema],
):
    response = sync_client.get(
        f"orders/{db_orders.results[1].id}/items/{db_order_items.results[1].id}"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
