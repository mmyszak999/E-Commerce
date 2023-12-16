from fastapi import status
from fastapi.testclient import TestClient

from src.apps.products.schemas import CategoryOutputSchema, ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.factories import UserRegisterSchemaFactory
from tests.test_core.conftest import db_categories, db_products, db_staff_user, db_user


def test_users_can_be_filtered_by_the_attributes(
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


def test_categories_can_be_filtered_by_the_attributes(
    sync_client: TestClient,
    staff_auth_headers: dict[str, str],
    db_categories: list[CategoryOutputSchema],
):
    pass
