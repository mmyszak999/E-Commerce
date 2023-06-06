from typing import Any

from fastapi import status
from fastapi.testclient import TestClient

from src.apps.orders.schemas import OrderOutputSchema
from src.apps.products.schemas import ProductOutputSchema

def test_authenticated_user_can_create_order(
    post_order: dict[str, Any],
    sync_client: TestClient,
    get_token_header: dict[str, str],
):
    response = sync_client.post("orders/", json=post_order, headers=get_token_header)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['user']['id'] == post_order['user_id']

def test_authenticated_user_can_get_orders(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_orders: list[OrderOutputSchema]
):
    response = sync_client.get("orders/", headers=get_token_header)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == len(db_orders)

def test_authenticated_user_get_single_order(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_orders: list[OrderOutputSchema]
):
    response = sync_client.get(f"orders/{db_orders[1].id}", headers=get_token_header)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_orders[1].id

def test_authenticated_user_can_update_order(
    sync_client: TestClient,
    update_order: dict[str, str],
    get_token_header: dict[str, str],
    db_orders: list[OrderOutputSchema]
):
    response = sync_client.patch(f"orders/{db_orders[0].id}", json=update_order, headers=get_token_header)
    
    assert response.status_code == status.HTTP_200_OK
    assert [response.json()["products"][0]['id']] == update_order["product_ids"]

def test_authenticated_user_can_delete_order(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_orders: list[OrderOutputSchema]
):
    response = sync_client.delete(f"orders/{db_orders[0].id}", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
def test_authenticated_user_can_delete_all_orders(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_orders: list[OrderOutputSchema]
):
    response = sync_client.delete("orders/", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = sync_client.get("orders/", headers=get_token_header)
    assert len(response.json()['results']) == 0

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
    update_order: dict[str, str]
):
    response = sync_client.patch("orders/1", json=update_order)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_delete_order(
    sync_client: TestClient
):
    response = sync_client.delete("orders/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
