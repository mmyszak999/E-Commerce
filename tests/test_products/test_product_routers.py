from typing import Any

from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import ProductOutputSchema, CategoryOutputSchema

def test_authenticated_user_can_create_product(
    post_product: dict[str, Any],
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_categories: list[CategoryOutputSchema]
):
    response = sync_client.post("products/", json=post_product, headers=get_token_header)
    assert response.status_code == status.HTTP_201_CREATED

def test_authenticated_user_can_get_products(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_products: list[ProductOutputSchema]
):
    response = sync_client.get("products/", headers=get_token_header)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['results']) == len(db_products)

def test_authenticated_user_get_single_product(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_products: list[ProductOutputSchema]
):
    response = sync_client.get(f"products/{db_products[1].id}", headers=get_token_header)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_products[1].id

def test_authenticated_user_can_update_product(
    sync_client: TestClient,
    update_product: dict[str, str],
    get_token_header: dict[str, str],
    db_products: list[ProductOutputSchema]
):
    response = sync_client.patch(f"products/{db_products[0].id}", json=update_product, headers=get_token_header)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == update_product["name"]
    assert response.json()["price"] == update_product["price"]

def test_authenticated_user_can_delete_category(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_products: list[CategoryOutputSchema]
):
    response = sync_client.delete(f"products/{db_products[0].id}", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
def test_authenticated_user_can_delete_all_products(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_products: list[ProductOutputSchema]
):
    response = sync_client.delete("products/", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = sync_client.get("products/", headers=get_token_header)
    assert len(response.json()['results']) == 0

def test_anonymous_user_cannot_get_products(
    sync_client: TestClient,
):
    response = sync_client.get("products/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_get_single_product(
    sync_client: TestClient,
):
    response = sync_client.get("products/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"

def test_anonymous_user_cannot_update_product(
    sync_client: TestClient,
    update_product: dict[str, str]
):
    response = sync_client.patch("products/1", json=update_product)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_delete_product(
    sync_client: TestClient
):
    response = sync_client.delete("products/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
