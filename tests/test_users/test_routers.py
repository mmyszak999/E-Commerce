from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.apps.user.models.user import User
from src.apps.user.schemas.user import UserRegisterSchema, UserUpdateSchema
from src.apps.user.services.user import register_user, update_single_user


def test_register_single_user(
    register_data: dict[str, Any],
    sync_client: TestClient
):
    response = sync_client.post("users/register", json=register_data)
    print(register_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_get_all_users(
    sync_client: TestClient,
    sync_session: Session
):
    response = sync_client.get("users/")
    amount_of_users_from_db = sync_session.query(User).count()
    assert len(response.json()) == amount_of_users_from_db
    assert response.status_code == status.HTTP_200_OK
    

def test_get_single_user(
    sync_client: TestClient,
    sync_session: Session
):
    user_from_db = sync_session.query(User).order_by(User.id.desc()).first()
    response = sync_client.get(f"users/{user_from_db.id}/")
    assert response.json()["id"] == user_from_db.id
    assert response.status_code == status.HTTP_200_OK

def test_update_single_user(
    update_db_user: UserRegisterSchema,
    update_user_schema: UserUpdateSchema,
    sync_client: TestClient,
    sync_session: Session
):
    user = register_user(sync_session, update_db_user)
    db_user = sync_session.query(User).filter(User.username == user.username).first()
    update_single_user(sync_session, update_user_schema, user_id=db_user.id)
    response = sync_client.get(f"users/{db_user.id}/")
    assert response.json()["username"] == update_user_schema.username

def test_delete_single_user(
    sync_client: TestClient,
    sync_session: Session
):
    user_from_db = sync_session.query(User).order_by(User.id.desc()).first()
    response = sync_client.delete(f"users/{user_from_db.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT