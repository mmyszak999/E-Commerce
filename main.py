from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from src.apps.user.models.models import User
from src.apps.user.schemas.schemas import (
    UserInputSchema,
    UserOutputSchema,
    UserRegisterSchema
)
from src.apps.user.services import crud
from src.apps.user.database import SessionLocal, engine

User.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users", response_model=UserOutputSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserRegisterSchema, db : Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist")
    return db_user

@app.get("/users", response_model=list[UserOutputSchema], status_code=status.HTTP_200_OK)
def get_users(skip: int = 0, limit: int = 100,db: Session = Depends(get_db)):
    db_users = crud.get_users(db, skip=skip, limit=limit)
    return db_users

@app.get("/users/{user_id}", response_model=UserOutputSchema, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=UserOutputSchema, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: UserInputSchema, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user, user_id)
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)








