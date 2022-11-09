from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, PendingRollbackError

from src.apps.user.models.user import User
from src.apps.user.schemas.user import UserRegisterSchema, UserUpdateSchema
from src.apps.user.services.user import register_user, update_single_user


def test_create_user_with_occupied_email(
    sync_session: Session,
    occupied_email_schema: UserRegisterSchema
):
    with pytest.raises(IntegrityError) as exc:
        register_user(sync_session, occupied_email_schema)


def test_create_user_with_occupied_username(
    sync_session: Session,
    occupied_username_schema: UserRegisterSchema
):
    with pytest.raises((PendingRollbackError)) as exc:
        register_user(sync_session, occupied_username_schema)









