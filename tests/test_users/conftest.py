from datetime import date
from typing import Any

import pytest
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from src.apps.user.services import register_user, get_single_user
from src.apps.user.schemas import UserRegisterSchema, UserUpdateSchema, UserOutputSchema
from src.apps.user.models import User

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

user_register_data = {
        "first_name": "janusz",
        "last_name": "pawlacz",
        "email": "janpaw@mail.com",
        "birth_date": "2020-07-12",
        "username": "janpaw22",
        "password": "janusz1488",
        "password_repeat": "janusz1488"
        }

user_update_data = {
        "first_name": list_of_user_register_schemas[0].first_name,
        "last_name": list_of_user_register_schemas[0].last_name,
        "email": "kowal@mailedit.com",
        "birth_date": "1983-10-12",
        "username": list_of_user_register_schemas[0].username
        }
    
@pytest.fixture(scope="package", autouse=True)
def db_users(sync_session: Session):
    return [register_user(sync_session, user) for user in list_of_user_register_schemas]

@pytest.fixture(scope="module")
def register_data() -> dict[str, str]:
    return user_register_data

@pytest.fixture(scope="module")
def login_data() -> dict[str, str]:
    return {
        "username": user_register_data['username'],
        "password": user_register_data['password']
    }

@pytest.fixture(scope="module")
def get_token_header(sync_session: Session, db_users: list[UserOutputSchema]) -> dict[str, str]:
    user_schema = get_single_user(sync_session, db_users[0].id)
    access_token = AuthJWT().create_access_token(subject=user_schema.json())
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="module")
def update_data() -> dict[str, str]:
    return user_update_data

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