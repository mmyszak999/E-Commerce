from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for

from src.settings.db_settings import settings
from src.apps.user.database import Base
from src.apps.user.services.user import register_user
from src.apps.user.schemas.user import UserRegisterSchema, UserUpdateSchema
from src.apps.user.utils.get_db import get_db
from main import app


@pytest.fixture(scope="session")
def sync_engine():
    DATABASE_URL = 'postgresql://{}:{}@{}:{}/test'.format(
        settings.POSTGRES_USER, settings.POSTGRES_PASSWORD, 
        settings.POSTGRES_HOST,settings.POSTGRES_PORT
        )

    engine = create_engine(DATABASE_URL)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def sync_session(sync_engine: Engine):
    connection = sync_engine.connect()
    transaction = connection.begin()
    sync_session = Session(bind=connection)

    connection.begin_nested()

    @listens_for(sync_session, "after_transaction_end")
    def restart_savepoint(session=sync_session, transaction=transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    yield sync_session

    sync_session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def sync_client():
    with TestClient(app=app, base_url="http://localhost:8000/api/") as sync_client:
        yield sync_client


@pytest.fixture(autouse=True)
def override_get_sync_session(sync_session: Session):
    app.dependency_overrides[get_db] = lambda: sync_session
    yield

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

@pytest.fixture(autouse=True)
def create_test_users(sync_session: Session):
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
def update_db_user() -> UserRegisterSchema:
    db_user = UserRegisterSchema(
        first_name = 'donald',
        last_name = 'trump',
        email = 'maga@gmail.com',
        birth_date = date(1950,1,1),
        username = 'donaldjtrump',
        password = 'buildthewall',
        password_repeat = 'buildthewall'
    )

    return db_user

@pytest.fixture(scope="module")
def update_user_schema() -> UserUpdateSchema:
    user_schema = UserUpdateSchema(
        first_name = 'donald_2',
        last_name = 'trump_2',
        email = 'maga_updated@gmail.com',
        birth_date = date(1951,2,2),
        username = 'donaldjtrump_updated',
        password = 'buildthewall'
    )

    return user_schema


@pytest.fixture(scope='module')
def incorrect_passwords_dict() -> dict[str, str]:
    return  {
        "first_name": "average",
        "last_name": "joe",
        "email": "avjoe@mail.com",
        "birth_date": "1980-07-12",
        "username": "imjoe",
        "password": "wearethesame",
        "password_repeat": "wearenotthesame"
    }

@pytest.fixture(scope='module')
def date_from_future_dict() -> dict[str, str]:
    return  {
        "first_name": "future",
        "last_name": "man",
        "email": "pluto@mail.com",
        "birth_date": "2137-04-20",
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
        birth_date = date(1974,4,24),
        username = 'karkraw',
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



