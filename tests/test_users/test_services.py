import pytest
import copy
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from src.apps.user.services import (
    register_user, get_single_user,
    delete_single_user, get_all_users,
    update_single_user
)
from src.apps.user.schemas import UserRegisterSchema, UserOutputSchema, UserUpdateSchema
from src.apps.user.models import User
from src.core.exceptions import (
    DoesNotExist,
    AlreadyExists,
    IsOccupied,
    AuthException
)
from src.core.pagination.models import PageParams


def test_register_user_that_already_exists(
    sync_session: Session,
    register_existing_user_data: UserRegisterSchema,
    db_users: list[UserOutputSchema]
):
    with pytest.raises(AlreadyExists) as exc:
        register_user(sync_session, register_existing_user_data)


def test_create_user_with_occupied_email(
    sync_session: Session,
    register_data: dict[str, Any],
    db_users: list[UserOutputSchema]
):
    user_data = copy.copy(register_data)
    user_data['email'] = db_users[0].email
    with pytest.raises(AlreadyExists) as exc:
        register_user(sync_session, UserRegisterSchema(**user_data))


def test_create_user_with_occupied_username(
    sync_session: Session,
    register_data: dict[str, Any],
    db_users: list[UserOutputSchema]
):
    user_data = copy.copy(register_data)
    user_data['username'] = db_users[0].username
    with pytest.raises(AlreadyExists) as exc:
        register_user(sync_session, UserRegisterSchema(**user_data))


def test_if_only_one_user_was_returned(
    sync_session: Session,
    db_users: list[UserOutputSchema]
):
    user = get_single_user(sync_session, db_users[1].id)

    assert type(user) == UserOutputSchema

def test_raise_exception_while_getting_nonexistent_user(
    sync_session: Session,
    db_users: list[UserOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        get_single_user(sync_session, len(db_users)+2)


def test_if_multiple_users_were_returned(
    sync_session: Session,
    db_users: list[UserOutputSchema]
):
    users = get_all_users(sync_session, PageParams(page=1, size=5))
    assert len(users.results) == len(db_users)

def test_raise_exception_while_updating_nonexistent_user(
    sync_session: Session,
    update_data: dict[str, Any],
    db_users: list[UserOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        update_single_user(sync_session, UserUpdateSchema(**update_data), len(db_users)+2)


def test_if_user_can_update_their_username_to_occupied_one(
    sync_session: Session,
    update_data: dict[str, Any],
    db_users: list[UserOutputSchema]
):
    user_data = copy.copy(update_data)
    user_data['username'] = db_users[1].username
    with pytest.raises(IsOccupied):
        update_single_user(sync_session, UserUpdateSchema(**user_data), db_users[0].id)


def test_if_user_can_update_their_email_to_occupied_one(
    sync_session: Session,
    update_data: dict[str, Any],
    db_users: list[UserOutputSchema]
):
    user_data = copy.copy(update_data)
    user_data['email'] = db_users[1].email
    with pytest.raises(IsOccupied):
        update_single_user(sync_session, UserUpdateSchema(**user_data), db_users[0].id)


def test_raise_exception_while_deleting_nonexistent_user(
    sync_session: Session,
    db_users: list[UserOutputSchema]
):
    with pytest.raises(DoesNotExist) as exc:
        delete_single_user(sync_session, len(db_users)+2)
