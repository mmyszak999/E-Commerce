import pytest
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.user.models import User
from src.apps.user.schemas import UserOutputSchema
from src.apps.user.services import (delete_all_users, get_single_user,
                                    register_user)
from src.core.factories import UserRegisterSchemaFactory

DB_USER_SCHEMA = UserRegisterSchemaFactory.build(
    password="vgo39845n", password_repeat="vgo39845n"
)


@pytest.fixture
def db_user(sync_session: Session) -> UserOutputSchema:
    return register_user(sync_session, DB_USER_SCHEMA)


@pytest.fixture
def auth_headers(sync_session: Session, db_user: UserOutputSchema) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(db_user.id)
    return {"Authorization": f"Bearer {access_token}"}
