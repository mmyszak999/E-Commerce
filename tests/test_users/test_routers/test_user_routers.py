from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.user.schemas import UserLoginInputSchema, UserOutputSchema
from src.core.factories import UserRegisterSchemaFactory, AddressInputSchemaFactory
from tests.test_products.conftest import db_categories, db_products
from tests.test_users.conftest import DB_USER_SCHEMA


def test_if_user_was_created_successfully(sync_client: TestClient):
    new_address = AddressInputSchemaFactory().generate()
    register_data = UserRegisterSchemaFactory().generate(address=new_address)
    response = sync_client.post("users/register", data=register_data.json())
    assert response.status_code == status.HTTP_201_CREATED


def test_if_user_was_logged_correctly(
    sync_client: TestClient, db_user: UserOutputSchema
):
    login_data = UserLoginInputSchema(
        email=DB_USER_SCHEMA.email, password=DB_USER_SCHEMA.password
    )
    response = sync_client.post("users/login", json=login_data.dict())
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_user_cannot_be_logged_without_activated_account(sync_client: TestClient):
    new_address = AddressInputSchemaFactory().generate()
    register_data = UserRegisterSchemaFactory().generate(address=new_address)
    response = sync_client.post("users/register", data=register_data.json())
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["is_active"] == False

    login_data = UserLoginInputSchema(
        email=register_data.email, password=register_data.password
    )
    response = sync_client.post("users/login", json=login_data.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_staff_can_get_users(
    sync_client: TestClient, staff_auth_headers: dict[str, str]
):
    response = sync_client.get("users/", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2


def test_staff_can_get_single_user(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    response = sync_client.get(f"users/{db_user.id}", headers=staff_auth_headers)
    
    assert response.json()["id"] == db_user.id
    assert response.status_code == status.HTTP_200_OK
    

def test_authenticated_user_can_get_single_user(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    response = sync_client.get(f"users/{db_user.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_can_get_their_account_info_page(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    response = sync_client.get("users/me", headers=auth_headers)

    assert response.json()["id"] == db_user.id
    assert response.status_code == status.HTTP_200_OK


def test_authenticated_user_cannot_get_their_account_info_page_with_inactive_account(
    sync_client: TestClient,
):
    """
    in this case we assume the user obtained token in the other way
    than by login to the account
    """
    new_address = AddressInputSchemaFactory().generate()
    register_data = UserRegisterSchemaFactory().generate(address=new_address)
    response = sync_client.post("users/register", data=register_data.json())
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["is_active"] == False

    user_token = AuthJWT().create_access_token(register_data.email)
    user_auth_headers = {"Authorization": f"Bearer {user_token}"}

    response = sync_client.get("users/me", headers=user_auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


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
