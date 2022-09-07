import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from src.settings.db_settings import settings
from src.apps.user.utils import get_db
from main import app



DATABASE_URL = 'postgresql://{}:{}@{}:{}/test'.format(
        settings.POSTGRES_USER, settings.POSTGRES_PASSWORD, 
        settings.POSTGRES_HOST,settings.POSTGRES_PORT
        )

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    connection = engine.connect()

      # begin a non-ORM transaction
    connection.begin()

      # bind an individual Session to the connection
    db = Session(bind=connection)
      # db = Session(engine)

    yield db

    db.rollback()
    connection.close()


client = TestClient(app)