from fastapi import status
from fastapi.testclient import TestClient

from src.apps.user.schemas import UserOutputSchema
from src.apps.orders.schemas import OrderOutputSchema
from src.core.factories import UserRegisterSchemaFactory
from tests.test_users.conftest import DB_USER_SCHEMA


def test_if_user_was_created_successfully(sync_client: TestClient):
    register_data = UserRegisterSchemaFactory.build(
        password="mtdqwc241", password_repeat="mtdqwc241"
    )
    response = sync_client.post("users/register", data=register_data.json())
    assert response.status_code == status.HTTP_201_CREATED


def test_if_user_was_logged_correctly(
    sync_client: TestClient, db_user: UserOutputSchema
):
    login_data = {
        "username": DB_USER_SCHEMA.username,
        "password": DB_USER_SCHEMA.password,
    }
    response = sync_client.post("users/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_staff_can_get_users(
    sync_client: TestClient, staff_auth_headers: dict[str, str]
):
    response = sync_client.get("users/", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    print(response.json())
    assert response.json()["total"] == 2


def test_staff_can_get_single_user(
    sync_client: TestClient, staff_auth_headers: dict[str, str], db_user: UserOutputSchema
):
    response = sync_client.get(f"users/{db_user.id}", headers=staff_auth_headers)
    print(response.json())
    assert response.json()["id"] == db_user.id
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_get_their_account(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    response = sync_client.get("users/me", headers=auth_headers)

    assert response.json()["id"] == db_user.id
    assert response.status_code == status.HTTP_200_OK

"""
def test_staff_can_get_some_user_orders(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_user: list[UserOutputSchema],
    db_orders: list[OrderOutputSchema],
):
    response = sync_client.get(f"users/{db_user.id}/orders", headers=staff_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_orders)"""


def test_authenticated_user_can_update_their_account(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    update_data = {"username": "alex123"}
    response = sync_client.patch(
        f"users/{db_user.id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == update_data["username"]


def test_staff_can_delete_user(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    response = sync_client.delete(f"users/{db_user.id}", headers=staff_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_authenticated_user_cannot_get_users(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.get("users/", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_get_users(
    sync_client: TestClient,
):
    response = sync_client.get("users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_get_single_user(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema,
):
    response = sync_client.get(f"users/{db_user.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_get_single_user(
    sync_client: TestClient, db_user: UserOutputSchema
):
    response = sync_client.get(f"users/{db_user.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_get_their_account(
    sync_client: TestClient,
):
    response = sync_client.get("users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_delete_user(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.delete("users/1", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_delete_user(sync_client: TestClient):
    response = sync_client.delete("users/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
