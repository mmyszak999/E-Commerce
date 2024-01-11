from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import CategoryOutputSchema, ProductOutputSchema, InventoryOutputSchema
from src.core.factories import ProductInputSchemaFactory, InventoryInputSchemaFactory, ProductUpdateSchemaFactory


def test_staff_can_create_product(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    inventory_data = InventoryInputSchemaFactory().generate()
    product_data = ProductInputSchemaFactory().generate(
        category_ids=[db_categories[0].id], inventory=inventory_data
    )
    response = sync_client.post(
        "products/", data=product_data.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_authenticated_user_can_get_all_products(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
    auth_headers: dict[str, str],
):
    response = sync_client.get("products/", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_products)


def test_anonymous_user_can_get_all_products(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
):
    response = sync_client.get("products/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_products)


def test_anonymous_user_get_single_product(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
):
    response = sync_client.get(f"products/{db_products[1].id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_products[1].id


def test_staff_can_get_product_inventory(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    inventory_data = InventoryInputSchemaFactory().generate()
    product_data = ProductInputSchemaFactory().generate(
        category_ids=[db_categories[1].id], inventory=inventory_data
    )
    response = sync_client.post(
        "products/", data=product_data.json(), headers=staff_auth_headers
    )
    inventory_id = response.json()["inventory"]["id"]
    product_id = response.json()["id"]
    
    assert response.status_code == status.HTTP_201_CREATED
    
    response = sync_client.get(
        f"products/{product_id}/inventory", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == inventory_id
    

def test_staff_can_update_product(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    db_categories: list[CategoryOutputSchema]
):
    
    update_data = ProductUpdateSchemaFactory().generate(
        category_ids=[db_categories[0].id]
    )
    
    response = sync_client.patch(
        f"products/{db_products[0].id}",
        data=update_data.json(),
        headers=staff_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["categories"][0]["id"] == update_data.category_ids[0]


def test_staff_can_delete_product(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_products: list[CategoryOutputSchema],
):
    response = sync_client.delete(
        f"products/{db_products[0].id}", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_authenticated_user_cannot_update_product(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[CategoryOutputSchema],
):
    update_data = ProductUpdateSchemaFactory().generate()
    response = sync_client.patch(
        f"products/{db_products[0].id}", headers=auth_headers, data=update_data.json()
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_update_product(
    sync_client: TestClient,
):
    update_data = ProductUpdateSchemaFactory().generate()
    response = sync_client.patch("products/1", data=update_data.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_delete_product(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[CategoryOutputSchema],
):
    response = sync_client.delete(f"products/{db_products[0].id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_delete_product(
    sync_client: TestClient, db_products: list[CategoryOutputSchema]
):
    response = sync_client.delete(f"products/{db_products[0].id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
