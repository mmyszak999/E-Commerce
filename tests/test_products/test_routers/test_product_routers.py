from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import (
    CategoryOutputSchema,
    InventoryOutputSchema,
    ProductOutputSchema,
)
from src.core.factories import (
    InventoryInputSchemaFactory,
    ProductInputSchemaFactory,
    ProductUpdateSchemaFactory,
)


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
        "products/", content=product_data.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_staff_can_get_all_products_including_removed_ones(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
    auth_headers: dict[str, str],
    staff_auth_headers: dict[str, str]
):
    response = sync_client.patch(
        f"products/{db_products[0].id}/remove", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    response = sync_client.get("products/all", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_products)


def test_authenticated_user_cannot_get_all_products(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
    auth_headers: dict[str, str],
):
    response = sync_client.get("products/all", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_get_all_products(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
):
    response = sync_client.get("products/all")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    

def test_authenticated_user_can_get_available_products(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
    auth_headers: dict[str, str],
    staff_auth_headers: dict[str, str],
):
    response = sync_client.patch(
        f"products/{db_products[0].id}/remove", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    response = sync_client.get("products/", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_products) - 1


def test_anonymous_user_can_get_available_products(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
    auth_headers: dict[str, str],
    staff_auth_headers: dict[str, str],
):
    response = sync_client.patch(
        f"products/{db_products[0].id}/remove", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    response = sync_client.get("products/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_products) - 1


def test_authenticated_user_can_get_single_product(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
):
    response = sync_client.get(f"products/{db_products[1].id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_products[1].id


def test_anonymous_user_can_get_single_product(
    sync_client: TestClient,
    db_products: list[ProductOutputSchema],
):
    response = sync_client.get(f"products/{db_products[1].id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_products[1].id


def test_staff_user_gets_whole_data_about_removed_product(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    staff_auth_headers: dict[str, str],
):
    response = sync_client.patch(
        f"products/{db_products[0].id}/remove", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    response = sync_client.get(f"products/all/{db_products[0].id}", headers=staff_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["removed_from_store"] == True
    assert response.json()["price"] == db_products[0].price
    
    
def test_authenticated_user_gets_limited_data_about_removed_product(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    staff_auth_headers: dict[str, str],
):
    response = sync_client.patch(
        f"products/{db_products[0].id}/remove", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    response = sync_client.get(f"products/{db_products[0].id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == db_products[0].description
    assert response.json()["name"] == db_products[0].name


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
        "products/", content=product_data.json(), headers=staff_auth_headers
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
    db_categories: list[CategoryOutputSchema],
):
    update_data = ProductUpdateSchemaFactory().generate(
        category_ids=[db_categories[0].id]
    )

    response = sync_client.patch(
        f"products/{db_products[0].id}",
        content=update_data.json(),
        headers=staff_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["categories"][0]["id"] == update_data.category_ids[0]


def test_staff_can_remove_product_from_store(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_products: list[CategoryOutputSchema],
):
    response = sync_client.patch(
        f"products/{db_products[0].id}/remove", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    response = sync_client.get(
        f"products/all/{db_products[0].id}", headers=staff_auth_headers
    )
    assert response.json()["removed_from_store"] == True


def test_authenticated_user_cannot_update_product(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[CategoryOutputSchema],
):
    update_data = ProductUpdateSchemaFactory().generate()
    response = sync_client.patch(
        f"products/{db_products[0].id}",
        headers=auth_headers,
        content=update_data.json(),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_update_product(
    sync_client: TestClient, db_products: list[CategoryOutputSchema]
):
    update_data = ProductUpdateSchemaFactory().generate()
    response = sync_client.patch(f"products/{db_products[0].id}", content=update_data.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_remove_product_from_store(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[CategoryOutputSchema],
):
    response = sync_client.patch(f"products/{db_products[0].id}/remove", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_remove_product_from_store(
    sync_client: TestClient, db_products: list[CategoryOutputSchema]
):
    response = sync_client.patch(f"products/{db_products[0].id}/remove")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"
