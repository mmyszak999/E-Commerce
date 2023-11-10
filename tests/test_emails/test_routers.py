from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.user.schemas import UserOutputSchema
from src.core.factories import UserRegisterSchemaFactory
from src.core.utils import generate_confirm_token
from tests.test_users.conftest import auth_headers, db_user


def test_confirm_email_change(
    sync_client: TestClient, db_user: UserOutputSchema, auth_headers: dict[str, str]):
    new_email = "new_email@mail.com"
    confirm_token = generate_confirm_token([db_user.email, new_email])
    response = sync_client.post(
        f"email/confirm-email-change/?token={confirm_token}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Email updated successfully!"
    
    new_token = AuthJWT().create_access_token(new_email)
    new_auth_headers = {"Authorization": f"Bearer {new_token}"}
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
    
    new_user_token = AuthJWT().create_access_token(register_data.email)
    new_user_auth_headers = {"Authorization": f"Bearer {new_user_token}"}
    
    new_email = "new_email@mail.com"
    confirm_token = generate_confirm_token([db_user.email, new_email])
    
    response = sync_client.post(
        f"email/confirm-email-change/?token={confirm_token}", headers=new_user_auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Your email is different from the email requested to be changed!'
    