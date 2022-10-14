from gc import get_debug
from typing import Any
from urllib import response
import pytest

from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session
from httpx import Client, ASGITransport, AsyncClient

from src.apps.user.utils.get_db import get_db
from tests.test_users.conftest import Client as test_client
from main import app


@pytest.fixture(scope="module")
def register_data():
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
def override_get_sync_session(sync_session: Session):
    app.dependency_overrides[get_db] = lambda: sync_session
    yield


def test_user_can_register(
    register_data: dict[str, Any],
    sync_client: Client
):
    response = sync_client.post("http://localhost:8000/api/users/register", json=register_data)
    print(response.status_code)

    assert response.status_code == 201


