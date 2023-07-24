from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
import pytest
from sqlalchemy.orm import Session

from src.apps.user.schemas import UserOutputSchema, UserUpdateSchema
from src.apps.emails.services import send_confirmation_mail_change_email
from src.apps.user.services import register_user
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied, ServiceException
from src.core.factories import UserRegisterSchemaFactory, EmailUpdateSchemaFactory
from src.core.pagination.models import PageParams

from tests.test_users.conftest import DB_USER_SCHEMA


def test_if_user_cannot_send_confirmation_mail_change_email_when_new_email_equals_the_current_one(
    sync_session: Session, db_user: UserOutputSchema
):
    token = AuthJWT().create_access_token(db_user.email)
    schema = EmailUpdateSchemaFactory.build(email=db_user.email, new_email=db_user.email)
    
    with pytest.raises(ServiceException):
        send_confirmation_mail_change_email(schema, sync_session, token, BackgroundTasks)


def test_if_user_cannot_send_confirmation_mail_change_email_when_new_email_is_occupied(
    sync_session: Session, db_user: UserOutputSchema
):  
    user_data = UserRegisterSchemaFactory.build(
        email="mail@mail.com", password="testtest", password_repeat="testtest"
    )
    new_user = register_user(sync_session, user_data)
    
    token = AuthJWT().create_access_token(new_user.email)
    email_update_data = EmailUpdateSchemaFactory.build(email=new_user.email, new_email=db_user.email)
    
    with pytest.raises(IsOccupied):
        send_confirmation_mail_change_email(email_update_data, sync_session, token, BackgroundTasks)
        