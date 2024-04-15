from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.user.schemas import (
    AddressOutputSchema,
    AddressUpdateSchema,
    UserOutputSchema,
)
from src.core.factories import AddressInputSchemaFactory
from tests.test_users.conftest import DB_ADDRESS_SCHEMAS, db_addresses, db_user


def test_staff_can_get_all_addresses(
    sync_client: TestClient, staff_auth_headers: dict[str, str]
):
    response = sync_client.get("addresses/", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2


def test_staff_can_get_single_address(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_addresses: list[AddressOutputSchema],
):
    response = sync_client.get(
        f"addresses/{db_addresses.results[0].id}", headers=staff_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_addresses.results[0].id


def test_staff_can_update_single_address(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_addresses: list[AddressOutputSchema],
):
    update_data = AddressInputSchemaFactory().generate()
    response = sync_client.patch(
        f"addresses/{db_addresses.results[0].id}",
        headers=staff_auth_headers,
        content=update_data.json(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["city"] == update_data.city


def test_anonymous_user_cannot_get_addresses(
    sync_client: TestClient,
):
    response = sync_client.get("addresses/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_get_single_address(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_addresses: list[AddressOutputSchema],
):
    response = sync_client.get(
        f"addresses/{db_addresses.results[0].id}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_authenticated_user_cannot_update_address(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_addresses: list[AddressOutputSchema],
):
    update_data = AddressInputSchemaFactory().generate()
    response = sync_client.patch(
        f"addresses/{db_addresses.results[0].id}",
        content=update_data.json(),
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_update_address(
    sync_client: TestClient,
    db_addresses: list[AddressOutputSchema],
):
    update_data = AddressInputSchemaFactory().generate()
    response = sync_client.patch(
        f"addresses/{db_addresses.results[0].id}", content=update_data.json()
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
