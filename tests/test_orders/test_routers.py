from fastapi import status
from fastapi.testclient import TestClient

from src.apps.orders.schemas import OrderOutputSchema
from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.factories import OrderInputSchemaFactory


def test_authenticated_user_can_create_order(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    order_data = OrderInputSchemaFactory.build(
        user_id=db_user.id, product_ids=[db_products[1].id]
    )
    response = sync_client.post("orders/", data=order_data.json(), headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user"]["id"] == order_data.user_id


def test_authenticated_user_can_get_orders(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get("orders/", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_orders)


def test_authenticated_user_get_single_order(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get(f"orders/{db_orders[1].id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_orders[1].id


def test_authenticated_user_can_update_order(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
    db_products: list[ProductOutputSchema],
    db_user: list[UserOutputSchema],
):
    update_data = OrderInputSchemaFactory.build(
        user_id=db_user.id, product_ids=[db_products[2].id]
    )
    response = sync_client.patch(
        f"orders/{db_orders[2].id}", data=update_data.json(), headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert [response.json()["products"][0]["id"]] == update_data.product_ids


def test_authenticated_user_can_delete_order(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.delete(f"orders/{db_orders[0].id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_authenticated_user_can_delete_all_orders(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.delete("orders/", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = sync_client.get("orders/", headers=auth_headers)
    assert response.json()["total"] == 0


def test_anonymous_user_cannot_get_orders(
    sync_client: TestClient,
):
    response = sync_client.get("orders/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_get_single_order(
    sync_client: TestClient,
):
    response = sync_client.get("orders/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_update_order(
    sync_client: TestClient,
):
    update_data = OrderInputSchemaFactory.build()
    response = sync_client.patch("orders/1", data=update_data.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_delete_order(sync_client: TestClient):
    response = sync_client.delete("orders/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
