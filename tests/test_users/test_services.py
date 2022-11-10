import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from sqlalchemy import delete, select, update
from src.apps.user.services.user import register_user, get_single_user, delete_single_user
from src.apps.user.schemas.user import UserRegisterSchema, UserOutputSchema
from src.apps.user.models.user import User
from src.apps.user.exceptions import UserDoesNotExistException, UserAlreadyExists


def test_password_hashed_correctly(
    sync_session: Session,
    hash_test_schema: UserRegisterSchema
):
    created_user = register_user(sync_session, hash_test_schema)
    user_from_db = sync_session.execute(select(User).filter(User.id == created_user.id)).scalar()
    assert user_from_db.password != hash_test_schema.password
    assert type(created_user) == UserOutputSchema

    with pytest.raises(AttributeError) as exc:
        user_from_db.password_repeat


def test_register_user_that_already_exists(
    sync_session: Session,
    hash_test_schema: UserRegisterSchema
):
    with pytest.raises(UserAlreadyExists) as exc:
        register_user(sync_session, hash_test_schema)


def test_create_user_with_occupied_email(
    sync_session: Session,
    occupied_email_schema: UserRegisterSchema
):
    with pytest.raises(UserAlreadyExists) as exc:
        register_user(sync_session, occupied_email_schema)


def test_create_user_with_occupied_username(
    sync_session: Session,
    occupied_username_schema: UserRegisterSchema
):
    with pytest.raises(UserAlreadyExists) as exc:
        register_user(sync_session, occupied_username_schema)


def test_raise_exception_while_getting_nonexistent_user(
    sync_session: Session
):
    with pytest.raises(UserDoesNotExistException) as exc:
        get_single_user(sync_session, 999999)


def test_raise_exception_while_deleting_nonexistent_user(
    sync_session: Session
):
    with pytest.raises(UserDoesNotExistException) as exc:
        delete_single_user(sync_session, 666666)















