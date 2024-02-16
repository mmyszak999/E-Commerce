import subprocess

import pytest
from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.user.schemas import (
    AddressOutputSchema,
    UserOutputSchema,
    UserRegisterSchema,
)
from src.apps.user.services.address_services import get_all_addresses
from src.apps.user.services.user_services import register_user_base
from src.core.factories import AddressInputSchemaFactory, UserRegisterSchemaFactory
from src.core.pagination.models import PageParams

DB_ADDRESS_SCHEMAS = [AddressInputSchemaFactory().generate() for _ in range(2)]

DB_USER_SCHEMA = UserRegisterSchemaFactory().generate(address=DB_ADDRESS_SCHEMAS[0])

DB_STAFF_USER_SCHEMA = UserRegisterSchemaFactory().generate(
    address=DB_ADDRESS_SCHEMAS[1]
)


def register_user_without_activation(
    sync_session: Session,
    user_schema: UserRegisterSchema,
    is_active: bool = True,
    is_staff: bool = False,
):
    new_user, new_address = register_user_base(sync_session, user_schema)
    new_user.is_active = is_active
    new_user.is_staff = is_staff
    sync_session.add(new_user)
    sync_session.commit()

    new_address.user_id = new_user.id
    sync_session.add(new_address)

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
def db_addresses(sync_session: Session) -> list[AddressOutputSchema]:
    return get_all_addresses(sync_session, PageParams())


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
