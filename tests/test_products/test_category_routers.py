from typing import Any

from fastapi import status
from fastapi.testclient import TestClient

from tests.test_products.conftest import CategoryInputSchema


def test_authenticated_user_can_create_category(
    post_category: dict[str, Any],
    sync_client: TestClient,
    get_token_header: dict[str, str]
):
    response = sync_client.post("categories/", json=post_category, headers=get_token_header)
    assert response.status_code == status.HTTP_201_CREATED

def test_authenticated_user_can_get_categories(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_categories: list[CategoryInputSchema]
):
    sync_client.delete(f"categories/{len(db_categories)+1}", headers=get_token_header) # deletes the previously created user
    response = sync_client.get("categories/", headers=get_token_header)
    print(response.json())
    
    assert len(response.json()['results']) == len(db_categories)
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_get_single_category(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_categories: list[CategoryInputSchema]
):
    response = sync_client.get(f"categories/{db_categories[1].id}", headers=get_token_header)
    assert response.json()["id"] == db_categories[1].id
    assert response.status_code == status.HTTP_200_OK

def test_authenticated_user_can_update_category(
    sync_client: TestClient,
    update_category: dict[str, str],
    get_token_header: dict[str, str],
    db_categories: list[CategoryInputSchema]
):
    response = sync_client.put(f"categories/{db_categories[0].id}", json=update_category, headers=get_token_header)
    
    assert response.json()["name"] == update_category["name"]

def test_authenticated_user_can_delete_category(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_categories: list[CategoryInputSchema]
):
    response = sync_client.delete(f"categories/{db_categories[0].id}", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT




