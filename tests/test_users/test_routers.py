from typing import Any
import json

from fastapi import status
from fastapi.testclient import TestClient

from tests.test_users.conftest import UserOutputSchema
from src.core.factories import UserFactory


def test_create_user(
    sync_client: TestClient,
):
    register_data = UserFactory.build(password="mtdqwc241", password_repeat="mtdqwc241")
    response = sync_client.post("users/register", json=json.loads(register_data.json()))
    assert response.status_code == status.HTTP_201_CREATED
    
def test_login_user(
    sync_client: TestClient,
    login_data: dict[str, str],
    db_user: UserOutputSchema
):
    response = sync_client.post("users/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_authenticated_user_can_get_users(
    sync_client: TestClient,
    access_token: dict[str, str],
    db_user: UserOutputSchema
):
    response = sync_client.get("users/", headers=access_token)
    
    assert len(response.json()['results']) == len([db_user])
    assert response.status_code == status.HTTP_200_OK
    
def test_authenticated_user_can_get_single_user(
    sync_client: TestClient,
    access_token: dict[str, str],
    db_user: UserOutputSchema
):
    response = sync_client.get(f"users/{db_user.id}", headers=access_token)
    assert response.json()["id"] == db_user.id
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_get_their_account(
    sync_client: TestClient,
    access_token: dict[str, str],
    db_user: UserOutputSchema
):
    response = sync_client.get(f"users/me", headers=access_token)
    assert response.json()["id"] == db_user.id
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_update_user(
    sync_client: TestClient,
    access_token: dict[str, str],
    db_user: UserOutputSchema
):
    update_data = {"first_name": "alex"}
    response = sync_client.patch(f"users/{db_user.id}", json=update_data, headers=access_token)
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == update_data["first_name"]


def test_authenticated_user_can_delete_user(
    sync_client: TestClient,
    access_token: dict[str, str],
    db_user: UserOutputSchema
):
    response = sync_client.delete(f"users/{db_user.id}", headers=access_token)
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
    response = sync_client.get("users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_update_user(
    sync_client: TestClient,
):
    update_data = {"first_name": "alex"}
    response = sync_client.patch("users/1", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_delete_user(
    sync_client: TestClient
):
    response = sync_client.delete("users/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"