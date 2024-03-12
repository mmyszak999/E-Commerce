from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.orders.schemas import (
    CartOutputSchema,
    CartInputSchema
)
from src.apps.user.schemas import UserOutputSchema
from src.core.factories import CartInputSchemaFactory
from tests.test_orders.conftest import db_carts
from tests.test_users.conftest import db_user, db_staff_user, staff_auth_headers, auth_headers


def test_authenticated_user_can_create_cart(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    create_data = CartInputSchemaFactory().generate(user_id=db_user.id)
    response = sync_client.post("carts/", headers=auth_headers, data=create_data.json())
 
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user_id"] == db_user.id


def test_staff_user_can_get_all_carts(
    sync_client: TestClient, staff_auth_headers: dict[str, str], db_carts: list[CartOutputSchema]
):
    response = sync_client.get("carts/all", headers=staff_auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2
    
    
def test_staff_user_can_get_single_cart(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_carts: list[CartOutputSchema], db_user: UserOutputSchema
):
    response = sync_client.get(f"carts/{db_carts.results[1].id}", headers=staff_auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user_id"] == db_user.id

def test_authenticated_can_get_their_carts(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_carts: list[CartOutputSchema], db_user: UserOutputSchema
):
    response = sync_client.get(f"carts/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1

def test_staff_can_delete_cart(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_carts: list[CartOutputSchema]
):
    response = sync_client.delete(f"carts/{db_carts.results[0].id}", headers=staff_auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    

def test_anonymous_user_cannot_create_cart(
    sync_client: TestClient, db_user: UserOutputSchema
):
    create_data = CartInputSchemaFactory().generate(user_id=db_user.id)
    response = sync_client.post("carts/", data=create_data.json())
 
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticated_user_cannot_get_all_carts(
    sync_client: TestClient, auth_headers: dict[str, str], db_carts: list[CartOutputSchema]
):
    response = sync_client.get("carts/all", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_get_single_cart(
    sync_client: TestClient, db_carts: list[CartOutputSchema]
):
    response = sync_client.get(f"carts/{db_carts.results[0].id}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_anonymous_user_cannot_get_their_carts(
    sync_client: TestClient, db_carts: list[CartOutputSchema]
):
    response = sync_client.get(f"carts/")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticated_cannot_delete_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_carts: list[CartOutputSchema]
):
    response = sync_client.delete(f"carts/{db_carts.results[0].id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND



