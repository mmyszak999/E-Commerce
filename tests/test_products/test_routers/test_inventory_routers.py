from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import InventoryOutputSchema, ProductOutputSchema
from src.core.factories import InventoryInputSchemaFactory


def test_staff_can_get_all_inventories(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema],
    staff_auth_headers: dict[str, str],
):
    response = sync_client.get("inventories/", headers=staff_auth_headers)
    print(db_inventories)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == db_inventories.total


def test_staff_get_single_inventory(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema],
):
    response = sync_client.get(
        f"inventories/{db_inventories.results[1].id}", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_inventories.results[1].id


def test_staff_can_update_inventory(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema],
):
    update_data = InventoryInputSchemaFactory().generate()
    response = sync_client.patch(
        f"inventories/{db_inventories.results[0].id}",
        data=update_data.json(),
        headers=staff_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["quantity"] == update_data.quantity


def test_anonymous_user_cannot_get_inventories(
    sync_client: TestClient,
):
    response = sync_client.get("inventories/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_get_single_inventory(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema],
):
    response = sync_client.get(
        f"inventories/{db_inventories.results[0].id}", headers=auth_headers
    )
    print(response.json())
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_authenticated_user_cannot_update_inventory(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema],
):
    update_data = InventoryInputSchemaFactory().generate()
    response = sync_client.patch(
        f"inventories/{db_inventories.results[0].id}",
        data=update_data.json(),
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_update_inventory(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema]
):
    update_data = InventoryInputSchemaFactory().generate()
    response = sync_client.patch(
        f"inventories/{db_inventories.results[0].id}", data=update_data.json()
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
