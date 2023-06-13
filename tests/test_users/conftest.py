from datetime import date
from typing import Any
import json

import pytest
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from src.apps.user.services import register_user, get_single_user, delete_all_users
from src.apps.user.schemas import UserRegisterSchema, UserUpdateSchema, UserOutputSchema
from src.apps.user.models import User
from src.core.factories import UserFactory

DB_USER_SCHEMA = UserFactory.build(password="vgo39845n", password_repeat="vgo39845n")

@pytest.fixture
def db_user(sync_session: Session):
    return register_user(sync_session, DB_USER_SCHEMA)

@pytest.fixture
def login_data() -> dict[str, str]:
    return {
        "username": DB_USER_SCHEMA.username,
        "password": DB_USER_SCHEMA.password
    }

@pytest.fixture
def access_token(sync_session: Session, db_user: UserOutputSchema) -> dict[str, str]:
    user_schema = get_single_user(sync_session, db_user.id)
    access_token = AuthJWT().create_access_token(subject=user_schema.json())
    return {"Authorization": f"Bearer {access_token}"}
