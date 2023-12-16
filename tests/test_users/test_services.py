import pytest
from sqlalchemy.orm import Session

from src.apps.user.schemas import UserOutputSchema, UserUpdateSchema
from src.apps.user.services import (
    activate_account,
    delete_single_user,
    get_all_users,
    get_single_user,
    update_single_user,
)
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    ServiceException,
)
from src.core.factories import UserRegisterSchemaFactory
from src.core.pagination.models import PageParams
from tests.test_users.conftest import DB_USER_SCHEMA, register_user_without_activation


def test_register_user_that_already_exists(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(AlreadyExists):
        register_user_without_activation(sync_session, DB_USER_SCHEMA)


def test_create_user_with_occupied_email(
    sync_session: Session, db_user: UserOutputSchema
):
    user_data = UserRegisterSchemaFactory().generate(
        email=db_user.email, password="testtest", password_repeat="testtest"
    )
    with pytest.raises(AlreadyExists):
        register_user_without_activation(sync_session, user_data)


def test_create_user_with_occupied_username(
    sync_session: Session, db_user: UserOutputSchema
):
    user_data = UserRegisterSchemaFactory().generate(
        username=db_user.username, password="testtest", password_repeat="testtest"
    )
    with pytest.raises(AlreadyExists):
        register_user_without_activation(sync_session, user_data)


def test_raise_exception_when_activating_account_when_user_does_not_exist(
    sync_session: Session,
):
    with pytest.raises(DoesNotExist):
        activate_account(sync_session, email="nonexistent@mail.com")


def test_raise_exception_when_activating_account_that_is_already_activated(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(ServiceException):
        activate_account(sync_session, email=db_user.email)


def test_if_only_one_user_was_returned(
    sync_session: Session, db_user: UserOutputSchema
):
    user = get_single_user(sync_session, db_user.id)

    assert user.id == db_user.id


def test_raise_exception_while_getting_nonexistent_user(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(DoesNotExist):
        get_single_user(sync_session, db_user.id + 2222222222)


def test_if_multiple_users_were_returned(
    sync_session: Session, db_user: UserOutputSchema
):
    users = get_all_users(sync_session, PageParams(page=1, size=5))
    assert users.total == 2


def test_raise_exception_while_updating_nonexistent_user(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(DoesNotExist):
        update_data = {"first_name": "name"}
        update_single_user(sync_session, UserUpdateSchema(**update_data), 888888888)


def test_if_user_can_update_their_username_to_occupied_one(
    sync_session: Session, db_user: UserOutputSchema
):
    user = register_user_without_activation(
        sync_session,
        UserRegisterSchemaFactory().generate(
            password="testtestx", password_repeat="testtestx"
        ),
    )
    update_data = {"username": db_user.username}

    with pytest.raises(IsOccupied):
        update_single_user(sync_session, UserUpdateSchema(**update_data), user.id)


def test_raise_exception_while_deleting_nonexistent_user(
    sync_session: Session, db_user: UserOutputSchema
):
    with pytest.raises(DoesNotExist):
        delete_single_user(sync_session, db_user.id + 2222222222)
