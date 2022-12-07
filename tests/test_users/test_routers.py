from typing import Any

from fastapi import status
from fastapi.testclient import TestClient


def test_create_user(
    register_data: dict[str, Any],
    sync_client: TestClient,
):
    response = sync_client.post("users/register", json=register_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_get_users(
    sync_client: TestClient,
    get_token_header: dict[str, str]
):
    response = sync_client.get("users/", headers=get_token_header)
    assert len(response.json()) == 4
    assert response.status_code == status.HTTP_200_OK
    

def test_get_user(
    sync_client: TestClient,
    get_token_header: dict[str, str]
):
    response = sync_client.get(f"users/{1}", headers=get_token_header)
    assert response.json()["id"] == 1
    assert response.status_code == status.HTTP_200_OK


def test_update_user(
    sync_client: TestClient,
    update_data: dict[str, str],
    get_token_header: dict[str, str]
):
    response = sync_client.put(f"users/{1}", json=update_data, headers=get_token_header)
    assert response.json()["first_name"] == update_data["first_name"]


def test_delete_user(
    sync_client: TestClient,
    get_token_header: dict[str, str]
):
    response = sync_client.delete(f"users/{1}", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT