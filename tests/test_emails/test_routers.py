from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.user.schemas import UserOutputSchema
from src.core.factories import UserRegisterSchemaFactory
from tests.test_orders.conftest import db_orders
from tests.test_users.conftest import auth_headers, db_user


def test_confirm_email_change(
    sync_client: TestClient, db_user: UserOutputSchema, auth_headers: dict[str, str]):
    token = AuthJWT().create_access_token(db_user.email)
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


def test_request_user_cannot_confirm_change_of_not_their_email(
    sync_client: TestClient, db_user: UserOutputSchema, auth_headers: dict[str, str]
):
    register_data = UserRegisterSchemaFactory.build(
        email="email@mail.com", password="mtdqwc241", password_repeat="mtdqwc241"
    )
    response = sync_client.post("users/register", data=register_data.json())
    assert response.status_code == status.HTTP_201_CREATED
    
    token = AuthJWT().create_access_token(register_data.email)
    new_email = "new_email@mail.com"
    response = sync_client.post(
        f"email/confirm-email-change/?token={token}&new_email={new_email}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "You only can change email address assigned to your account!"
    