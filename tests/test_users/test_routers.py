from typing import Any

from fastapi import status
from fastapi.testclient import TestClient


def test_register_single_user(
    register_data: dict[str, Any],
    sync_client: TestClient,
):

    response = sync_client.post("users/register", json=register_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_get_all_users(
    sync_client: TestClient
):
    response = sync_client.get("users/")
    print(response.json())
    assert len(response.json()) == 4
    assert response.status_code == status.HTTP_200_OK
    

def test_get_single_user(
    sync_client: TestClient,
):
    response = sync_client.get(f"users/{2}")
    assert response.json()["id"] == 2
    assert response.status_code == status.HTTP_200_OK

def test_update_single_user(
    sync_client: TestClient,
    update_data: dict[str, str]
):
    response = sync_client.put(f"users/{3}", json=update_data)
    assert response.json()["username"] == update_data["username"]

def test_delete_single_user(
    sync_client: TestClient,
):
    response = sync_client.delete(f"users/{3}")
    assert response.status_code == status.HTTP_204_NO_CONTENT