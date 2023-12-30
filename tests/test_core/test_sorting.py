from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.models import Category
from src.apps.products.schemas import CategoryOutputSchema, ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.factories import (
    CategoryInputSchemaFactory,
    ProductInputSchemaFactory,
    UserRegisterSchemaFactory,
)
from tests.test_core.conftest import db_categories, db_products, db_staff_user, db_user


def test_users_can_be_sorted_by_their_attributes(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_user: UserOutputSchema,
):
    new_user_1 = UserRegisterSchemaFactory().generate(
        email="zoomer1@mail.com", last_name="zimmermann", username="aabc-guy1123"
    )
    new_user_2 = UserRegisterSchemaFactory().generate(
        email="zoomer2@mail.com", last_name="zimmermann"
    )
    response = sync_client.post("users/register", data=new_user_1.json())
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.post("users/register", data=new_user_2.json())
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.get(
        "users/?sort=last_name__desc,email__desc", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"][0]["email"] == new_user_2.email
    assert response.json()["results"][1]["email"] == new_user_1.email

    response = sync_client.get("users/?sort=username__asc", headers=staff_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"][0]["username"] == new_user_1.username


def test_categories_can_be_sorted_by_their_attributes(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_categories: CategoryOutputSchema,
):
    new_category_1 = CategoryInputSchemaFactory().generate(name="aa-category")
    new_category_2 = CategoryInputSchemaFactory().generate(name="zz-category")
    response = sync_client.post(
        "categories/", data=new_category_1.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.post(
        "categories/", data=new_category_2.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.get(
        "categories/?sort=name__desc", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"][-1]["name"] == new_category_1.name
    assert response.json()["results"][0]["name"] == new_category_2.name


def test_products_can_be_sorted_by_their_attributes(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_products: ProductOutputSchema,
    db_categories: list[CategoryOutputSchema],
):
    new_category = CategoryInputSchemaFactory().generate(name="zz-category")
    response = sync_client.post(
        "categories/", data=new_category.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.get(
        f"categories/?name__eq={new_category.name}", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    new_category_id = response.json()["results"][0]["id"]

    new_product_1 = ProductInputSchemaFactory().generate(category_ids=[new_category_id])
    new_product_2 = ProductInputSchemaFactory().generate(
        category_ids=[db_categories[0].id, db_categories[2].id], price=0.09
    )
    response = sync_client.post(
        "products/", data=new_product_1.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.post(
        "products/", data=new_product_2.json(), headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = sync_client.get("products/?sort=categories__name__desc")
    assert response.json()["results"][0]["categories"][0]["name"] == new_category.name

    response = sync_client.get("products/?sort=price__asc")
    assert response.json()["results"][0]["price"] == float(new_product_2.price)
