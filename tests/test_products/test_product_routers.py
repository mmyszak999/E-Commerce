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
    
    assert len(response.json()['results']) == len(db_products)
    assert response.status_code == status.HTTP_200_OK





