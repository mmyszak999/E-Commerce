from fastapi import status
from fastapi.testclient import TestClient

from src.apps.user.schemas import UserOutputSchema
from tests.test_users.conftest import (
    auth_headers,
    create_superuser,
    db_staff_user,
    db_user,
    staff_auth_headers,
    superuser_auth_headers,
)


def test_superuser_can_get_all_superusers(
    sync_client: TestClient, superuser_auth_headers: dict[str, str]
):
    response = sync_client.get("admin/superusers", headers=superuser_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1


def test_non_superuser_cannot_get_all_superusers(
    sync_client: TestClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
):
    response = sync_client.get("admin/superusers", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_staff_can_get_all_staff_users(
    sync_client: TestClient, staff_auth_headers: dict[str, str]
):
    response = sync_client.get("admin/staff-users", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2


def test_non_staff_user_cannot_get_all_staff_users(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.get("admin/superusers", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_superuser_can_grant_staff_permissions(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    response = sync_client.patch(
        f"admin/grant-staff-permissions/{db_user.id}",
        headers=superuser_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Staff status has been granted successfully"


def test_non_superuser_cannot_grant_staff_permissions(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    response = sync_client.patch(
        f"admin/grant-staff-permissions/{db_user.id}", headers=staff_auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_superuser_can_revoke_staff_permissions(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_staff_user: UserOutputSchema,
):
    response = sync_client.patch(
        f"admin/revoke-staff-permissions/{db_staff_user.id}",
        headers=superuser_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Staff status has been revoked successfully"

    response = sync_client.get(
        f"users/{db_staff_user.id}", headers=superuser_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_staff"] == False


def test_non_superuser_cannot_revoke_staff_permissions(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_staff_user: UserOutputSchema,
):
    response = sync_client.patch(
        f"admin/revoke-staff-permissions/{db_staff_user.id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
