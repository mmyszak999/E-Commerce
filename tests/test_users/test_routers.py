from fastapi import status
from fastapi.testclient import TestClient

from src.apps.user.schemas import UserOutputSchema
from src.core.factories import UserRegisterSchemaFactory, EmailUpdateSchemaFactory
from tests.test_orders.conftest import db_orders
from tests.test_products.conftest import db_categories, db_products
from tests.test_users.conftest import DB_USER_SCHEMA


def test_create_user(sync_client: TestClient):
    register_data = UserRegisterSchemaFactory.build(
        password="mtdqwc241", password_repeat="mtdqwc241"
    )
    response = sync_client.post("users/register", data=register_data.json())
    assert response.status_code == status.HTTP_201_CREATED


def test_login_user(sync_client: TestClient, db_user: UserOutputSchema):
    login_data = {
        "email": DB_USER_SCHEMA.email,
        "password": DB_USER_SCHEMA.password,
    }
    response = sync_client.post("users/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_authenticated_user_can_get_users(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    response = sync_client.get("users/", headers=auth_headers)

    assert response.json()["total"] == 1
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_get_single_user(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    response = sync_client.get(f"users/{db_user.id}", headers=auth_headers)
    assert response.json()["id"] == db_user.id
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_get_their_account(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    response = sync_client.get("users/me", headers=auth_headers)
    assert response.json()["id"] == db_user.id
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_update_user(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    update_data = {"username": "alex123"}
    response = sync_client.patch(
        f"users/{db_user.id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == update_data["username"]


def test_authenticated_user_can_send_email_change_confirmation_mail(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    update_data = EmailUpdateSchemaFactory.build(
        password=DB_USER_SCHEMA.password, email=db_user.email, new_email="mail@mail.com")
    response = sync_client.post(
        f"users/change-email", data=update_data.json(), headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Email change confirmation mail has been sent to the new email address!"


def test_authenticated_user_can_delete_user(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    response = sync_client.delete(f"users/{db_user.id}", headers=auth_headers)
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


def test_anonymous_user_cannot_send_email_change_confirmation_email(
    sync_client: TestClient
):
    update_data = EmailUpdateSchemaFactory.build(new_email="mail@mail.com")
    response = sync_client.post(
        f"users/change-email", data=update_data.json()
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_delete_user(sync_client: TestClient):
    response = sync_client.delete("users/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
