from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.user.schemas import UserOutputSchema
from src.core.factories import EmailUpdateSchemaFactory, generate_user_register_schema
from src.core.utils import generate_confirm_token
from tests.test_users.conftest import auth_headers, db_user


def test_user_can_activate_their_account_via_activation_link(
    sync_client: TestClient, db_user: UserOutputSchema
):
    register_data = generate_user_register_schema()
    response = sync_client.post("users/register", data=register_data.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['is_active'] == False
    
    token = generate_confirm_token([register_data.email])
    response = sync_client.post(f"email/confirm-account-activation/{token}")
    assert (
        response.json()["message"]
        == "Account activated successfully!"
    )
    
    activated_user_token = AuthJWT().create_access_token(register_data.email)
    activated_user_auth_headers = {"Authorization": f"Bearer {activated_user_token}"}
    
    response = sync_client.get("users/me", headers=activated_user_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] == True
    

def test_authenticated_user_can_send_email_change_confirmation_mail(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    update_data = EmailUpdateSchemaFactory.build(
        email=db_user.email, new_email="mail@mail.com"
    )
    response = sync_client.post(
        "email/change-email", data=update_data.json(), headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"]
        == "Email change confirmation mail has been sent to the new email address!"
    )


def test_authenticated_user_cannot_send_email_change_confirmation_mail_to_change_not_their_email(
    sync_client: TestClient, auth_headers: dict[str, str], db_user: UserOutputSchema
):
    register_data = generate_user_register_schema()
    response = sync_client.post("users/register", data=register_data.json())

    assert response.status_code == status.HTTP_201_CREATED

    update_data = EmailUpdateSchemaFactory.build(
        email=register_data.email, new_email="new_email@mail.com"
    )
    response = sync_client.post(
        "email/change-email", data=update_data.json(), headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_anonymous_user_cannot_send_email_change_confirmation_email(
    sync_client: TestClient,
):
    update_data = EmailUpdateSchemaFactory.build(new_email="mail@mail.com")
    response = sync_client.post(f"email/change-email", data=update_data.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing Authorization Header"


def test_authenticated_user_can_confirm_email_change(
    sync_client: TestClient, db_user: UserOutputSchema, auth_headers: dict[str, str]
):
    new_email = "new_email@mail.com"
    confirm_token = generate_confirm_token([db_user.email, new_email])
    response = sync_client.post(
        f"email/confirm-email-change/{confirm_token}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Email updated successfully!"

    new_token = AuthJWT().create_access_token(new_email)
    new_auth_headers = {"Authorization": f"Bearer {new_token}"}
    response = sync_client.get("users/me", headers=new_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == new_email


def test_authenticated_user_cannot_confirm_change_of_not_their_email(
    sync_client: TestClient, db_user: UserOutputSchema, auth_headers: dict[str, str]
):
    register_data = generate_user_register_schema()
    response = sync_client.post("users/register", data=register_data.json())
    assert response.status_code == status.HTTP_201_CREATED

    new_user_token = AuthJWT().create_access_token(register_data.email)
    new_user_auth_headers = {"Authorization": f"Bearer {new_user_token}"}

    new_email = "new_email@mail.com"
    confirm_token = generate_confirm_token([db_user.email, new_email])

    response = sync_client.post(
        f"email/confirm-email-change/{confirm_token}", headers=new_user_auth_headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.json()["detail"]
        == "Your email is different from the email requested to be changed!"
    )


def test_anonymous_user_cannot_confirm_change_of_not_their_email(
    sync_client: TestClient, db_user: UserOutputSchema, auth_headers: dict[str, str]
):
    new_email = "new_email@mail.com"
    confirm_token = generate_confirm_token([db_user.email, new_email])

    response = sync_client.post(f"email/confirm-email-change/{confirm_token}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
