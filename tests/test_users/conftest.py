import subprocess

import pytest
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.user.schemas import UserOutputSchema
from src.apps.user.services import register_user
from src.core.factories import UserRegisterSchemaFactory

DB_USER_SCHEMA = UserRegisterSchemaFactory.build(
    password="vgo39845n", password_repeat="vgo39845n"
)

@pytest.fixture(autouse=True, scope='session')
def create_superuser():
    subprocess.run(["./app_scripts/create_superuser.sh", "test_db"])


@pytest.fixture
def db_user(sync_session: Session) -> UserOutputSchema:
    return register_user(sync_session, DB_USER_SCHEMA)


@pytest.fixture
def auth_headers(sync_session: Session, db_user: UserOutputSchema) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(db_user.username)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def superuser_auth_headers(
    sync_session: Session) -> dict[str, str]:
    access_token = AuthJWT().create_access_token("SuperUser")
    return {"Authorization": f"Bearer {access_token}"}
