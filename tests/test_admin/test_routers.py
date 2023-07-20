from fastapi import status
from fastapi.testclient import TestClient

from src.apps.user.schemas import UserOutputSchema
from tests.test_orders.conftest import db_orders
from tests.test_products.conftest import db_categories, db_products
from tests.test_users.conftest import (auth_headers, create_superuser, db_user,
                                       superuser_auth_headers)


def test_superuser_can_get_all_superusers(
    sync_client: TestClient, superuser_auth_headers: dict[str, str]
):
    response = sync_client.get("admin/superusers", headers=superuser_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1


def test_new_superuser_can_get_all_superusers(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
):
    sync_client.patch(
        f"admin/grant-superuser-permissions/user/{db_user.id}",
        headers=superuser_auth_headers,
    )

    response = sync_client.get("admin/superusers", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2


def test_non_superuser_cannot_get_all_superusers(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.get("admin/superusers", headers=auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_superuser_can_grant_superuser_status(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    response = sync_client.patch(
        f"admin/grant-superuser-permissions/user/{db_user.id}",
        headers=superuser_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"] == "Superuser status has been granted successfully"
    )


def test_non_superuser_cannot_grant_superuser_status(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.patch(
        "admin/grant-superuser-permissions/user/2", headers=auth_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_superuser_can_revoke_superuser_status(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    response = sync_client.patch(
        f"admin/grant-superuser-permissions/user/{db_user.id}",
        headers=superuser_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    response = sync_client.patch(
        f"admin/revoke-superuser-permissions/user/{db_user.id}",
        headers=superuser_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"] == "Superuser status has been revoked successfully"
    )


def test_non_superuser_cannot_revoke_superuser_status(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.patch(
        "admin/revoke-superuser-permissions/user/2", headers=auth_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
