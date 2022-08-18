from sqlalchemy.orm import Session

from users.src.apps.user.models.user_model import User
from users.src.apps.user.schemas.user_schema import (
    UserRegisterSchema,
    UserOutputSchema
)


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserRegisterSchema) -> UserOutputSchema:
    db_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        birth_date = user.birth_date,
        username = user.username,
        password = user.password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

