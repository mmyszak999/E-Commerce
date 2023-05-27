from datetime import date
from typing import Any

import pytest
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from src.apps.user.services import register_user, get_single_user, delete_all_users
from src.apps.user.schemas import UserRegisterSchema, UserUpdateSchema, UserOutputSchema
from src.apps.user.models import User

LIST_OF_USER_REGISTER_SCHEMAS = [
    UserRegisterSchema(
        first_name="jan",
        last_name="kowalski",
        email="kowaljan@mail.com",
        birth_date=date(2020,7,12),
        username="kowaljan2137",
        password="kowalkowal",
        password_repeat="kowalkowal"
    ),
    UserRegisterSchema(
        first_name="karol",
        last_name="krawczyk",
        email="krawczyk@gmail.com",
        birth_date=date(1965,6,18),
        username="karkraw",
        password="krawczyk1234",
        password_repeat="krawczyk1234"
    ),
    UserRegisterSchema(  
        first_name="norbert",
        last_name="gierczak",
        email="norbertgierczak@mail.com",
        birth_date=date(1999,4,20),
        username="jd123456",
        password="jdjdjdjd",
        password_repeat="jdjdjdjd")]

USER_REGISTER_DATA = {
        "first_name": "janusz",
        "last_name": "pawlacz",
        "email": "janpaw@mail.com",
        "birth_date": "2020-07-12",
        "username": "janpaw22",
        "password": "janusz1488",
        "password_repeat": "janusz1488"
        }

EXISTING_USER_DATA = LIST_OF_USER_REGISTER_SCHEMAS[0]

USER_UPDATE_DATA = {"email": "kowal@mailedit.com"}

@pytest.fixture
def register_existing_user_data() -> UserRegisterSchema:
    return EXISTING_USER_DATA

    
@pytest.fixture
def db_users(sync_session: Session):
    delete_all_users(sync_session)
    return [register_user(sync_session, user) for user in LIST_OF_USER_REGISTER_SCHEMAS]

@pytest.fixture
def register_data() -> dict[str, str]:
    return USER_REGISTER_DATA

@pytest.fixture
def login_data() -> dict[str, str]:
    return {
        "username": LIST_OF_USER_REGISTER_SCHEMAS[0].username,
        "password": LIST_OF_USER_REGISTER_SCHEMAS[0].password
    }

@pytest.fixture
def get_token_header(sync_session: Session, db_users: list[UserOutputSchema]) -> dict[str, str]:
    user_schema = get_single_user(sync_session, db_users[0].id)
    access_token = AuthJWT().create_access_token(subject=user_schema.json())
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def update_data() -> dict[str, str]:
    return USER_UPDATE_DATA
