from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from fastapi import status

from src.apps.user.models.user import User
from src.apps.user.schemas.user import (
    UserRegisterSchema,
    UserOutputSchema,
    UserInputSchema
)
from src.apps.user.utils.hash_password import hash_user_password


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session,limit: int = 100):
    return db.query(User).limit(limit).all()
    
def create_user(db: Session, user: UserRegisterSchema) -> UserOutputSchema:
    hash_user_password(user_schema=user)
    db_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        birth_date = user.birth_date,
        username = user.username,
        password = user.password
    )

    print(db_user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: UserInputSchema, user_id: int) -> UserOutputSchema:
    instance = get_user(db, user_id)
    for key, value in user.dict().items():
        setattr(instance, key, value)
    
    db.commit()
    db.refresh(instance)
    
    return UserOutputSchema.from_orm(instance)

def delete_user(db: Session, user_id: int):
    if_exists = select(User.id).filter(User.id == user_id)
    if db.scalar(if_exists) is None:
        return status.HTTP_404_NOT_FOUND

    statement = delete(User).filter(User.id == user_id)
    result = db.execute(statement)
    db.commit()
    return result