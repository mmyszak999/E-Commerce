from typing import Union

from fastapi import Depends, HTTPException, status, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.user.schemas.user import (
    UserInputSchema,
    UserOutputSchema,
    UserRegisterSchema
)
from src.apps.user.services import crud
from src.apps.user.utils.get_db import get_db

router = APIRouter(prefix="/users")

@router.post("/", response_model=UserOutputSchema, status_code=status.HTTP_201_CREATED, tags=["users"])
def create_user(user: UserRegisterSchema, db : Session = Depends(get_db)) -> UserOutputSchema:
    db_user = crud.create_user(db, user)
    return db_user

@router.get("/", response_model=list[UserOutputSchema], status_code=status.HTTP_200_OK, tags=["users"])
def get_users(db: Session = Depends(get_db)) -> list[UserOutputSchema]:
    db_users = crud.get_users(db)
    return db_users

@router.get("/{user_id}", response_model=UserOutputSchema, status_code=status.HTTP_200_OK, tags=["users"])
def get_user(user_id: int, db: Session = Depends(get_db)) -> Union[UserOutputSchema, int]:
    db_user = crud.get_user(db, user_id)
    return db_user

@router.put("/{user_id}", response_model=UserOutputSchema, status_code=status.HTTP_200_OK, tags=["users"])
def update_user(user_id: int, user: UserInputSchema, db: Session = Depends(get_db)) -> Union[UserOutputSchema, int]:
    db_user = crud.update_user(db, user, user_id)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response:
    crud.delete_user(db, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)