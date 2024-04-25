from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.orders.schemas import OrderOutputSchema
from src.apps.user.schemas import UserOutputSchema
from tests.test_orders.conftest import db_carts, db_orders
from tests.test_payments.conftest import db_payments, stripe_session, payment_intent
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)
from tests.test_products.conftest import db_categories, db_products
from src.apps.payments.schemas import PaymentOutputSchema
from src.core.pagination.schemas import PagedResponseSchema


def test_staff_user_can_get_all_payments(
    sync_client: TestClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    response = sync_client.get("payments/all", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert db_payments.total == response.json()["total"]


def test_authenticate_user_cannot_get_all_payments(
    sync_client: TestClient,
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    response = sync_client.get("payments/all", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_get_all_payments(
    sync_client: TestClient,
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    response = sync_client.get("payments/all")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticate_user_can_get_their_payments(
    sync_client: TestClient,
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    response = sync_client.get("payments/", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1
    assert response.json()["results"][0]["user"]["id"] == db_user.id


def test_staff_user_can_get_any_single_payment(
    sync_client: TestClient,
    db_staff_user: UserOutputSchema,
    staff_auth_headers: dict[str, str],
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    response = sync_client.get(f"payments/{db_payments.results[0].id}", headers=staff_auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_payments.results[0].id


def test_authenticated_user_can_get_only_their_single_payment(
    sync_client: TestClient,
    db_user: UserOutputSchema,
    auth_headers: dict[str, str],
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    response = sync_client.get(f"payments/{db_payments.results[0].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == db_payments.results[0].id
    
    response = sync_client.get(f"payments/{db_payments.results[1].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_anonymous_user_cannot_get_single_payment(
    sync_client: TestClient,
    db_payments: PagedResponseSchema[PaymentOutputSchema],
):
    response = sync_client.get(f"payments/{db_payments.results[0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
