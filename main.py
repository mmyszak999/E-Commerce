from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from users.src.apps.user.models import user_model
from users.src.apps.user.schemas import user_schema
from users.src.apps.user.services import user_services
from users.src.database import SessionLocal, engine

user_model.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=user_schema.UserOutputSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: user_schema.UserRegisterSchema, db : Session = Depends(get_db)):
    db_user = user_services.create_user(db, user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist")
    return db_user

@app.get("/users/", response_model=user_schema.UserOutputSchema)
def get_users(skip: int = 0, limit: int = 100,db: Session = Depends(get_db)):
    db_users = user_services.get_users(db, skip=skip, limit=limit)
    return db_users

@app.get("/users/{user_id}/", response_model=user_schema.UserOutputSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_services.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")
    return db_user





