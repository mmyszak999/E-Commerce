from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.user.schemas import UserOutputSchema
from tests.test_orders.conftest import db_orders
from tests.test_users.conftest import auth_headers, db_user


def test_confirm_email_change(
    sync_client: TestClient, db_user: UserOutputSchema, auth_headers: dict[str, str]):
    token = AuthJWT().create_access_token(db_user.email)
    print(db_user.email)
    new_email = "new_email@mail.com"
    response = sync_client.post(
        f"email/confirm-email-change/?token={token}&new_email={new_email}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Email updated successfully!"
    
    token = AuthJWT().create_access_token(new_email)
    new_auth_headers = {"Authorization": f"Bearer {token}"}
    response = sync_client.get("users/me", headers=new_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == new_email
    