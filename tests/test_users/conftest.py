from datetime import date
from typing import Any

import pytest
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from src.apps.user.services.user import register_user, get_single_user
from src.apps.user.schemas.user import UserRegisterSchema, UserUpdateSchema, UserOutputSchema
from src.apps.user.models.user import User


@pytest.fixture(scope="package", autouse=True)
def create_setup_users(sync_session: Session):
    list_of_user_register_schemas = [
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

    for user in list_of_user_register_schemas:
        register_user(sync_session, user)


@pytest.fixture(scope="module")
def register_data() -> dict[str, str]:
    return {
        "first_name": "jan",
        "last_name": "kowalski",
        "email": "kowal@mail.com",
        "birth_date": "2020-07-12",
        "username": "kowal2137",
        "password": "kowalkowal",
        "password_repeat": "kowalkowal"
        }


@pytest.fixture(scope="module")
def login_data() -> dict[str, str]:
    return {
        "username": "kowal2137",
        "password": "kowalkowal"
    }


@pytest.fixture(scope="module")
def get_token_header(sync_session: Session) -> dict[str, str]:
    user_schema = get_single_user(sync_session, 1)
    access_token = AuthJWT().create_access_token(subject=user_schema.json())
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="module")
def update_data() -> dict[str, str]:
    return {
        "first_name": "jan",
        "last_name": "kowalski",
        "email": "kowal@mail.com",
        "birth_date": "2020-07-12",
        "username": "kowalczyk2137"
        }


@pytest.fixture(scope='module')
def incorrect_passwords_dict() -> dict[str, Any]:
    return  {
        "first_name": "average",
        "last_name": "joe",
        "email": "avjoe@mail.com",
        "birth_date": date(1980,7,12),
        "username": "imjoe",
        "password": "wearethesame",
        "password_repeat": "wearenotthesame"
    }

@pytest.fixture(scope='module')
def date_from_future_dict() -> dict[str, Any]:
    return  {
        "first_name": "future",
        "last_name": "man",
        "email": "pluto@mail.com",
        "birth_date": date(2137,4,20),
        "username": "pluto",
        "password": "password_ok",
        "password_repeat": "password_ok"
    }

@pytest.fixture(scope="module")
def occupied_username_schema() -> UserRegisterSchema:
    user_schema = UserRegisterSchema(
        first_name = 'karol',
        last_name = 'krawczyk2',
        email = 'sth@gmail.com',
        birth_date = date(1974,4,25),
        username = "karkraw",
        password = 'password',
        password_repeat = 'password',
    )

    return user_schema

@pytest.fixture(scope="module")
def occupied_email_schema() -> UserRegisterSchema:
    user_schema = UserRegisterSchema(
        first_name = 'karol',
        last_name = 'krawczyk2',
        email = 'krawczyk@gmail.com',
        birth_date = date(1974,4,24),
        username = 'karkraw2',
        password = 'password',
        password_repeat = 'password',
    )

    return user_schema


@pytest.fixture(scope="module")
def hash_test_schema() -> UserRegisterSchema:
    user_schema = UserRegisterSchema(
        first_name = 'sleepy',
        last_name = 'joe',
        email = 'sleepyjoe@gmail.com',
        birth_date = date(1942,11,20),
        username = 'sleepyjoepotus',
        password = 'sleepyjoe',
        password_repeat = 'sleepyjoe'
    )

    return user_schema

@pytest.fixture(scope="module")
def register_user_data() -> UserRegisterSchema:
    user_schema = UserRegisterSchema(
        first_name = 'sleepy2',
        last_name = 'joe2',
        email = 'sleepyjoe2@gmail.com',
        birth_date = date(1943,11,20),
        username = 'sleepyjoepotus',
        password = 'sleepyjoe2',
        password_repeat = 'sleepyjoe2'
    )

    return user_schema

@pytest.fixture(scope="module")
def update_schema() -> UserUpdateSchema:
    user_schema = UserUpdateSchema(
        first_name = 'sleepy2',
        last_name = 'joe2',
        email = 'norbertgierczak@mail.com',
        birth_date = date(1943,11,20),
        username = "jd123456",
    )

    return user_schema