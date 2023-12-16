import subprocess

import pytest
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.user.schemas import UserOutputSchema, UserRegisterSchema
from src.apps.user.services import register_user_base
from src.core.factories import UserRegisterSchemaFactory

DB_USER_SCHEMA = UserRegisterSchemaFactory().generate()

DB_STAFF_USER_SCHEMA = UserRegisterSchemaFactory().generate()


def register_user_without_activation(
    sync_session: Session,
    user_schema: UserRegisterSchema,
    is_active: bool = True,
    is_staff: bool = False,
):
    new_user = register_user_base(sync_session, user_schema)
    new_user.is_active = is_active
    new_user.is_staff = is_staff
    sync_session.add(new_user)
    sync_session.commit()

    return UserOutputSchema.from_orm(new_user)


@pytest.fixture(scope="session", autouse=True)
def create_superuser():
    subprocess.run(["./app_scripts/create_superuser.sh", "test_db"])


@pytest.fixture
def db_user(sync_session: Session) -> UserOutputSchema:
    return register_user_without_activation(sync_session, DB_USER_SCHEMA)


@pytest.fixture
def db_staff_user(sync_session: Session) -> UserOutputSchema:
    return register_user_without_activation(
        sync_session, DB_STAFF_USER_SCHEMA, is_staff=True
    )


@pytest.fixture
def auth_headers(sync_session: Session, db_user: UserOutputSchema) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(db_user.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def staff_auth_headers(
    sync_session: Session, db_staff_user: UserOutputSchema
) -> dict[str, str]:
    access_token = AuthJWT().create_access_token(db_staff_user.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def superuser_auth_headers(sync_session: Session) -> dict[str, str]:
    access_token = AuthJWT().create_access_token("superuser@mail.com")
    return {"Authorization": f"Bearer {access_token}"}
