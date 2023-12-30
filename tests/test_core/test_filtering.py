from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import CategoryOutputSchema, ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.factories import (
    CategoryInputSchemaFactory,
    ProductInputSchemaFactory,
    UserRegisterSchemaFactory,
)
from tests.test_core.conftest import db_categories, db_products, db_staff_user, db_user


def test_users_can_be_filtered_by_their_attributes(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    new_user = UserRegisterSchemaFactory().generate(email="supertest@mail.com")
    response = sync_client.post("users/register", data=new_user.json())
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.get("users/?is_active__eq=True", headers=staff_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 3

    response = sync_client.get(
        f"users/?username__eq={new_user.username}", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1

    response = sync_client.get(
        f"users/?email__ge={new_user.email}&email__le=superuser@mail.com",
        headers=staff_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2


def test_categories_can_be_filtered_by_their_attributes(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    new_category_1 = CategoryInputSchemaFactory().generate("zazzz")
    new_category_2 = CategoryInputSchemaFactory().generate(name="zbzzz")
    response = sync_client.post(
        "categories/", data=new_category_1.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.post(
        "categories/", data=new_category_2.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.get(
        f"categories/?name__eq={new_category_2.name}", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1

    response = sync_client.get(
        f"categories/?name__ge={new_category_1.name}", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2


def test_products_can_be_filtered_by_their_attributes(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_products: list[ProductOutputSchema],
    db_categories: list[CategoryOutputSchema],
):
    new_product_1 = ProductInputSchemaFactory().generate(
        category_ids=[db_categories[0].id]
    )
    new_product_2 = ProductInputSchemaFactory().generate(
        category_ids=[db_categories[1].id, db_categories[2].id], price=0.09
    )
    response = sync_client.post(
        "products/", data=new_product_1.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.post(
        "products/", data=new_product_2.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.get(f"products/?price__le={new_product_2.price}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1

    response = sync_client.get(f"products/?name__eq={new_product_1.name}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1

    response = sync_client.get(
        f"products/?categories__id__eq={new_product_1.category_ids[0]}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 2

    response = sync_client.get(
        f"products/?categories__id__eq="
        f"{new_product_2.category_ids[0]},{new_product_2.category_ids[1]}&"
        f"name__eq={new_product_2.name}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1
