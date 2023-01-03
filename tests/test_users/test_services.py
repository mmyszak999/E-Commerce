import pytest
from sqlalchemy.orm import Session

from sqlalchemy import select
from src.apps.user.services import (
    register_user, get_single_user,
    delete_single_user, get_all_users,
    update_single_user
)
from src.apps.user.schemas import UserRegisterSchema, UserOutputSchema, UserUpdateSchema
from src.apps.user.models import User
from src.apps.user.exceptions import UserDoesNotExistException, UserAlreadyExists, FieldNameIsOccupied


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


def test_if_only_one_user_was_returned(
    sync_session: Session
):
    user = get_single_user(sync_session, 3)

    assert type(user) == UserOutputSchema


def test_raise_exception_while_getting_nonexistent_user(
    sync_session: Session
):
    with pytest.raises(UserDoesNotExistException) as exc:
        get_single_user(sync_session, 9999999999999)


def test_if_multiple_users_were_returned(
    sync_session: Session
):
    users = get_all_users(sync_session)
    print(users)
    assert len(users) > 1
    assert type(users) == list


def test_raise_exception_while_updating_nonexistent_user(
    sync_session: Session,
    update_schema: UserUpdateSchema
):
    with pytest.raises(UserDoesNotExistException) as exc:
        update_single_user(sync_session, update_schema, 92999999999919939999799)


def test_if_user_can_update_their_username_to_occupied_one(
    sync_session: Session,
    update_schema: UserUpdateSchema
):
    with pytest.raises(FieldNameIsOccupied):
        update_single_user(sync_session, update_schema, 4)


def test_if_user_can_update_their_email_to_occupied_one(
    sync_session: Session,
    update_schema: UserUpdateSchema
):
    with pytest.raises(FieldNameIsOccupied):
        update_single_user(sync_session, update_schema, 4)


def test_raise_exception_while_deleting_nonexistent_user(
    sync_session: Session
):
    with pytest.raises(UserDoesNotExistException) as exc:
        delete_single_user(sync_session, 666666666666666)
