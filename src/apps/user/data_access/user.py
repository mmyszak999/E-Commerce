from typing import Union

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from fastapi import status

from src.apps.user.models.user import User
from src.apps.user.schemas.user import (
    UserRegisterSchema,
    UserOutputSchema,
    UserInputSchema,
    UserUpdateSchema
)
from src.apps.user.utils.hash_password import hash_user_password


def get_all_users(session: Session) -> list[UserOutputSchema]:
    statement = select(User)
    instances = (session.execute(statement)).scalars()

    return [UserOutputSchema.from_orm(instance) for instance in instances]

def get_single_user(session: Session, user_id: int) -> Union[UserOutputSchema, int]:
    statement = select(User).filter(User.id == user_id)
    instance = session.execute(statement).scalar()

    return UserOutputSchema.from_orm(instance)

def register_user(session: Session, user: UserRegisterSchema) -> UserOutputSchema:
    hash_user_password(user_schema=user)
    db_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        birth_date = user.birth_date,
        username = user.username,
        password = user.password
    )
    session.add(db_user)
    session.commit()

    return UserOutputSchema.from_orm(db_user)

def update_single_user(session: Session, user: UserUpdateSchema, user_id: int) -> Union[UserOutputSchema, int]:
    statement = update(User).filter(User.id == user_id)
    statement = statement.values(**user.dict())

    session.execute(statement)
    session.commit()
    return get_single_user(session, user_id=user_id)

def delete_one_user(session: Session, user_id: int):
    if_exists = select(User.id).filter(User.id == user_id)
    if session.scalar(if_exists) is None:
        return status.HTTP_404_NOT_FOUND

    statement = delete(User).filter(User.id == user_id)
    result = session.execute(statement)
    session.commit()
    return result