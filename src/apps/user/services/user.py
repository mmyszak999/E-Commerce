from typing import Union

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from fastapi import status

from src.apps.user.schemas.user import (
    UserRegisterSchema,
    UserOutputSchema,
    UserUpdateSchema
)
from src.apps.user.models.user import User
from src.apps.user.utils.hash_password import hash_user_password
from src.apps.user.exceptions import user_does_not_exist_exception


def get_single_user(session: Session, user_id: int) -> UserOutputSchema:
    statement = select(User).filter(User.id == user_id).limit(1)
    if session.scalar(statement) is None:
        raise user_does_not_exist_exception

    instance = session.execute(statement).scalar()
    return UserOutputSchema.from_orm(instance)

def get_all_users(session: Session) -> list[UserOutputSchema]:
    statement = select(User)
    instances = (session.execute(statement)).scalars()

    return [UserOutputSchema.from_orm(instance) for instance in instances]
    
def register_user(session: Session, user: UserRegisterSchema) -> UserOutputSchema:
    user_data = user.dict()
    user_data.pop('password_repeat')
    user_data['password'] = hash_user_password(password=user_data.pop('password'))
    new_user = User(**user_data)

    session.add(new_user)
    session.commit()

    return UserOutputSchema.from_orm(new_user)

def update_single_user(session: Session, user: UserUpdateSchema, user_id: int) -> UserOutputSchema:
    statement = update(User).filter(User.id == user_id)
    statement = statement.values(**user.dict())

    session.execute(statement)
    session.commit()
    return get_single_user(session, user_id=user_id)

def delete_single_user(session: Session, user_id: int):
    if_exists = select(User.id).filter(User.id == user_id)
    if session.scalar(if_exists) is None:
        raise user_does_not_exist_exception

    statement = delete(User).filter(User.id == user_id)
    result = session.execute(statement)
    return result