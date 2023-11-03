from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import CategoryOutputSchema
from src.core.factories import CategoryInputSchemaFactory


def test_superuser_can_create_category(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
):
    create_data = CategoryInputSchemaFactory.build()
    response = sync_client.post(
        "categories/", data=create_data.json(), headers=superuser_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_superuser_can_get_categories(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    response = sync_client.get("categories/", headers=superuser_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_categories)


def test_authenticated_user_get_single_category(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    response = sync_client.get(
        f"categories/{db_categories[1].id}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_categories[1].id


def test_superuser_can_update_category(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    update_data = CategoryInputSchemaFactory.build()
    response = sync_client.patch(
        f"categories/{db_categories[0].id}",
        data=update_data.json(),
        headers=superuser_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == update_data.name


def test_superuser_can_delete_category(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    response = sync_client.delete(
        f"categories/{db_categories[0].id}", headers=superuser_auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_authenticated_user_cannot_get_categories(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.get("categories/", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_get_categories(
    sync_client: TestClient,
):
    response = sync_client.get("categories/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_get_single_category(
    sync_client: TestClient,
):
    response = sync_client.get("categories/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_update_category(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    update_data = CategoryInputSchemaFactory.build()
    response = sync_client.patch(
        "categories/1", data=update_data.json(), headers=auth_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_update_category(sync_client: TestClient):
    update_data = CategoryInputSchemaFactory.build()
    response = sync_client.patch("categories/1", data=update_data.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_delete_category(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.delete("categories/1", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_delete_category(sync_client: TestClient):
    response = sync_client.delete("categories/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"

