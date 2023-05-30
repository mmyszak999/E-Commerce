from typing import Any

from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import CategoryOutputSchema


def test_authenticated_user_can_create_category(
    post_category: dict[str, Any],
    sync_client: TestClient,
    get_token_header: dict[str, str],
):
    response = sync_client.post("categories/", json=post_category, headers=get_token_header)
    assert response.status_code == status.HTTP_201_CREATED

def test_authenticated_user_can_get_categories(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_categories: list[CategoryOutputSchema]
):
    response = sync_client.get("categories/", headers=get_token_header)
    
    assert len(response.json()['results']) == len(db_categories)
    assert response.status_code == status.HTTP_200_OK

def test_authenticated_user_get_single_category(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_categories: list[CategoryOutputSchema]
):
    response = sync_client.get(f"categories/{db_categories[1].id}", headers=get_token_header)
    assert response.json()["id"] == db_categories[1].id
    assert response.status_code == status.HTTP_200_OK

def test_authenticated_user_can_update_category(
    sync_client: TestClient,
    update_category: dict[str, str],
    get_token_header: dict[str, str],
    db_categories: list[CategoryOutputSchema]
):
    response = sync_client.patch(f"categories/{db_categories[0].id}", json=update_category, headers=get_token_header)
    
    assert response.json()["name"] == update_category["name"]

def test_authenticated_user_can_delete_category(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_categories: list[CategoryOutputSchema]
):
    response = sync_client.delete(f"categories/{db_categories[0].id}", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
def test_authenticated_user_can_delete_all_categories(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_categories: list[CategoryOutputSchema]
):
    response = sync_client.delete("categories/", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = sync_client.get("categories/", headers=get_token_header)
    assert len(response.json()['results']) == 0

def test_anonymous_user_cannot_get_categories(
    sync_client: TestClient,
):
    response = sync_client.get("categories/")
    assert len(response.json()) == 1
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_get_single_category(
    sync_client: TestClient,
):
    response = sync_client.get("categories/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"

def test_anonymous_user_cannot_update_category(
    sync_client: TestClient,
    update_category: dict[str, str]
):
    response = sync_client.patch("categories/1", json=update_category)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_delete_category(
    sync_client: TestClient
):
    response = sync_client.delete("categories/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
