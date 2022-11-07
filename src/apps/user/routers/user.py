from typing import Union

from fastapi import Depends, HTTPException, status, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.user.schemas.user import (
    UserUpdateSchema,
    UserOutputSchema,
    UserRegisterSchema
)
from src.apps.user.services.user import (
    register_user,
    get_single_user,
    get_all_users,
    delete_single_user,
    update_single_user
)
from src.apps.user.utils.get_db import get_db

router = APIRouter(prefix="/users")

@router.post("/register", response_model=UserOutputSchema, status_code=status.HTTP_201_CREATED, tags=["users"])
def create_user(user: UserRegisterSchema, db : Session = Depends(get_db)) -> UserOutputSchema:
    db_user = register_user(db, user)
    return db_user

@router.get("/", response_model=list[UserOutputSchema], status_code=status.HTTP_200_OK, tags=["users"])
def get_users(db: Session = Depends(get_db)) -> list[UserOutputSchema]:
    db_users = get_all_users(db)
    return db_users

@router.get("/{user_id}", response_model=UserOutputSchema, status_code=status.HTTP_200_OK, tags=["users"])
def get_user(user_id: int, db: Session = Depends(get_db)) -> Union[UserOutputSchema, int]:
    db_user = get_single_user(db, user_id)
    return db_user

@router.put("/{user_id}", response_model=UserOutputSchema, status_code=status.HTTP_200_OK, tags=["users"])
def update_user(user_id: int, user: UserUpdateSchema, db: Session = Depends(get_db)) -> Union[UserOutputSchema, int]:
    db_user = update_single_user(db, user, user_id)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response:
    delete_single_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)