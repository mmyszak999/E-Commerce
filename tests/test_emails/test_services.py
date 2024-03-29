import pytest
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.emails.services import (
    confirm_email_change_service,
    send_email_change_confirmation_mail,
    update_email,
)
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import DoesNotExist, IsOccupied, ServiceException
from src.core.factories import (
    AddressInputSchemaFactory,
    EmailUpdateSchemaFactory,
    UserRegisterSchemaFactory,
)
from src.core.utils.utils import generate_confirm_token
from tests.test_users.conftest import DB_USER_SCHEMA, register_user_without_activation


def test_if_user_cannot_send_email_change_confirmation_mail_when_new_email_equals_the_current_one(
    sync_session: Session, db_user: UserOutputSchema
):
    token = AuthJWT().create_access_token(db_user.email)
    schema = EmailUpdateSchemaFactory().generate(
        email=db_user.email, new_email=db_user.email
    )

    with pytest.raises(ServiceException):
        send_email_change_confirmation_mail(
            schema, sync_session, token, BackgroundTasks
        )


def test_if_user_cannot_send_email_change_confirmation_mail_when_new_email_is_occupied(
    sync_session: Session, db_user: UserOutputSchema
):
    new_address = AddressInputSchemaFactory().generate()
    user_data = UserRegisterSchemaFactory().generate(address=new_address)
    new_user = register_user_without_activation(sync_session, user_data)

    token = AuthJWT().create_access_token(new_user.email)
    email_update_data = EmailUpdateSchemaFactory().generate(
        email=new_user.email, new_email=db_user.email
    )

    with pytest.raises(IsOccupied):
        send_email_change_confirmation_mail(
            email_update_data, sync_session, token, BackgroundTasks
        )


def test_raise_exception_while_updating_email_of_nonexistent_user(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(DoesNotExist):
        update_email(
            sync_session,
            new_email="mail@mail.com",
            current_email="invalidmail@mail.com",
        )


def test_raise_exception_when_email_equals_new_email(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(ServiceException):
        update_email(sync_session, new_email=db_user.email, current_email=db_user.email)


def test_raise_exception_when_request_user_email_is_different_from_the_email_requested_to_change(
    sync_session: Session, db_user: UserOutputSchema
):
    request_user_email = "differentmail@mail.com"
    token = generate_confirm_token([db_user.email, "updated_email@mail.com"])
    with pytest.raises(ServiceException):
        confirm_email_change_service(sync_session, token, request_user_email)
