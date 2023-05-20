from typing import Any

from fastapi import status
from fastapi.testclient import TestClient

from tests.test_users.conftest import UserOutputSchema


def test_create_user(
    register_data: dict[str, Any],
    sync_client: TestClient,
):
    response = sync_client.post("users/register", json=register_data)
    assert response.status_code == status.HTTP_201_CREATED
    

def test_login_user(
    login_data: dict[str, str],
    sync_client: TestClient,
    get_token_header: dict[str, str]
):
    response = sync_client.post("users/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_get_users(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_users: list[UserOutputSchema]
):
    response = sync_client.get("users/", headers=get_token_header)
    
    assert len(response.json()['results']) == len(db_users)
    assert response.status_code == status.HTTP_200_OK
    

def test_authenticated_user_can_get_single_user(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_users: list[UserOutputSchema]
):
    response = sync_client.get(f"users/{db_users[1].id}", headers=get_token_header)
    assert response.json()["id"] == db_users[1].id
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_get_their_account(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_users: list[UserOutputSchema]
):
    response = sync_client.get(f"users/me", headers=get_token_header)
    assert response.json()["id"] == db_users[0].id
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_update_user(
    sync_client: TestClient,
    update_data: dict[str, str],
    get_token_header: dict[str, str],
    db_users: list[UserOutputSchema]
):
    response = sync_client.put(f"users/{db_users[0].id}", json=update_data, headers=get_token_header)
    assert response.json()["username"] == update_data["username"]


def test_authenticated_user_can_delete_user(
    sync_client: TestClient,
    get_token_header: dict[str, str],
    db_users: list[UserOutputSchema]
):
    response = sync_client.delete(f"users/{db_users[0].id}", headers=get_token_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_anonymous_user_cannot_get_users(
    sync_client: TestClient,
):
    response = sync_client.get("users/")
    assert len(response.json()) == 1
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_get_single_user(
    sync_client: TestClient,
):
    response = sync_client.get("users/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_get_their_account(
    sync_client: TestClient,
):
    response = sync_client.get("users/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_update_user(
    sync_client: TestClient,
    update_data: dict[str, str]
):
    response = sync_client.put("users/1", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_delete_user(
    sync_client: TestClient
):
    response = sync_client.delete("users/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"