import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for
from httpx import Client

from src.settings.db_settings import settings
from src.apps.user.utils import get_db
from src.apps.user.database import Base
from main import app


@pytest.fixture()
def db_engine():
    DATABASE_URL = 'postgresql://{}:{}@{}:{}/test'.format(
        settings.POSTGRES_USER, settings.POSTGRES_PASSWORD, 
        settings.POSTGRES_HOST,settings.POSTGRES_PORT
        )

    engine = create_engine(DATABASE_URL)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(engine: Engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    connection.begin_nested()

    listens_for(session, "after_transaction_end")
    def restart_savepoint(session=session, transaction=transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

client = TestClient(app=app)
"""@pytest.fixture(scope="function")
def client():
    with Client(app=app, base_url='127.0.0.1:8000/') as sync_client:
        yield sync_client"""

"""@pytest.fixture(scope="function")
def override_get_db(engine: Engine):
    connection = engine.connect()

      # begin a non-ORM transaction
    connection.begin()

      # bind an individual Session to the connection
    db = Session(bind=connection)
      # db = Session(engine)

    yield db

    db.rollback()
    connection.close()"""
