from fastapi import status, Depends
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.apps.user.schemas.user import (
    UserRegisterSchema,
    UserOutputSchema,
    UserUpdateSchema
)
from src.apps.user.models.user import User
from src.apps.user.utils.hash_password import passwd_context
from src.apps.user.exceptions import UserDoesNotExistException, UserAlreadyExists, FieldNameIsOccupied, AuthException


def hash_user_password(password: str) -> str:
    return passwd_context.hash(password)


def register_user(session: Session, user: UserRegisterSchema) -> UserOutputSchema:
    user_data = user.dict()
    user_data.pop('password_repeat')
    user_data['password'] = hash_user_password(password=user_data.pop('password'))

    username_check = session.execute(select(User).filter(User.username == user_data["username"]))
    if username_check.first():
        raise UserAlreadyExists

    email_check = session.execute(select(User).filter(User.email == user_data["email"]))
    if email_check.first():
        raise UserAlreadyExists

    new_user = User(**user_data)

    session.add(new_user)
    session.commit()

    return UserOutputSchema.from_orm(new_user)


def authenticate(username: str, password: str, session: Session) -> User:
    statement = select(User).filter(username == User.username).limit(1)
    user = session.scalar(statement)
    if user is None or not passwd_context.verify(password, user.password):
        raise AuthException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
            )
    return user


def get_single_user(session: Session, user_id: int) -> UserOutputSchema:
    statement = select(User).filter(User.id == user_id).limit(1)
    if session.scalar(statement) is None:
        raise UserDoesNotExistException

    instance = session.execute(statement).scalar()
    return UserOutputSchema.from_orm(instance)


def get_all_users(session: Session) -> list[UserOutputSchema]:
    statement = select(User)
    instances = session.execute(statement).scalars()

    return [UserOutputSchema.from_orm(instance) for instance in instances]
    

def update_single_user(session: Session, user: UserUpdateSchema, user_id: int) -> UserOutputSchema:
    if_exists = select(User.id).filter(User.id == user_id)
    searched_user = session.scalar(if_exists)
    if searched_user is None:
        raise UserDoesNotExistException

    """
    username_check = session.execute(select(User).filter(User.username == user.username))
    if username_check.first() and searched_user != user_id:
        raise FieldNameIsOccupied

    email_check = session.execute(select(User).filter(User.email == user.email))
    if email_check.first() and searched_user != user_id:
        raise FieldNameIsOccupied"""

    statement = update(User).filter(User.id == user_id).values(**user.dict())

    session.execute(statement)
    session.commit()
    return get_single_user(session, user_id=user_id)


def delete_single_user(session: Session, user_id: int):
    if_exists = select(User.id).filter(User.id == user_id)
    if session.scalar(if_exists) is None:
        raise UserDoesNotExistException

    statement = delete(User).filter(User.id == user_id)
    result = session.execute(statement)
    return result