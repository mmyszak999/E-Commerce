from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import CategoryOutputSchema, ProductOutputSchema
from src.core.factories import ProductInputSchemaFactory


def test_superuser_user_can_create_product(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    product_data = ProductInputSchemaFactory.build(category_ids=[db_categories[0].id])
    response = sync_client.post(
        "products/", data=product_data.json(), headers=superuser_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_superuser_can_get_products(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
):
    response = sync_client.get("products/", headers=superuser_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(db_products)


def test_authenticated_user_get_single_product(
    sync_client: TestClient,
    auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
):
    response = sync_client.get(f"products/{db_products[1].id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_products[1].id


def test_superuser_can_update_product(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    db_categories: list[CategoryOutputSchema],
):
    update_data = ProductInputSchemaFactory.build(
        name="test_name", price=14.88, category_ids=[db_categories[0].id]
    )
    response = sync_client.patch(
        f"products/{db_products[0].id}",
        data=update_data.json(),
        headers=superuser_auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == update_data.name
    assert response.json()["price"] == float(update_data.price)


def test_superuser_can_delete_product(
    sync_client: TestClient,
    superuser_auth_headers: dict[str, str],
    db_products: list[CategoryOutputSchema],
):
    response = sync_client.delete(
        f"products/{db_products[0].id}", headers=superuser_auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_authenticated_user_cannot_get_products(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.get("products/", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_get_products(
    sync_client: TestClient,
):
    response = sync_client.get("products/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert len(response.json()) == 1
    assert response.json()["detail"] == "Missing Authorization Header"


def test_anonymous_user_cannot_get_single_product(
    sync_client: TestClient,
):
    response = sync_client.get("products/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_update_product(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    update_data = ProductInputSchemaFactory.build()
    response = sync_client.patch(
        "products/1", headers=auth_headers, data=update_data.json()
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_update_product(
    sync_client: TestClient,
):
    update_data = ProductInputSchemaFactory.build()
    response = sync_client.patch("products/1", data=update_data.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_cannot_delete_product(
    sync_client: TestClient, auth_headers: dict[str, str]
):
    response = sync_client.delete("products/1", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_delete_product(sync_client: TestClient):
    response = sync_client.delete("products/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


