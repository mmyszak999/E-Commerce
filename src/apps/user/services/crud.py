from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from fastapi import status

from src.apps.user.models.user import User
from src.apps.user.schemas.user import (
    UserRegisterSchema,
    UserOutputSchema,
    UserInputSchema
)
from src.apps.user.data_access.user import (
    get_all_users,
    get_single_user,
    register_user,
    update_single_user,
    delete_one_user
)


def get_user(db: Session, user_id: int) -> UserOutputSchema:
    return get_single_user(db, user_id)

def get_users(db: Session) -> list[UserOutputSchema]:
    return get_all_users(db)
    
def create_user(db: Session, user: UserRegisterSchema) -> UserOutputSchema:
    return register_user(db, user)

def update_user(db: Session, user: UserInputSchema, user_id: int) -> UserOutputSchema:
    return update_single_user(db, user, user_id)

def delete_user(db: Session, user_id: int):
    delete_one_user(db, user_id=user_id)