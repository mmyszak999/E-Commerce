import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for

from src.settings.db_settings import settings
from src.apps.user.database import Base
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


@pytest.fixture(scope="package")
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