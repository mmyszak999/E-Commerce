from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.emails.services import send_confirmation_mail_change_email
from src.apps.emails.schemas import EmailChangeConfirmationSchema
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user


email_router = APIRouter(prefix="/email", tags=["emails"])


@email_router.get(
    "/confirm-email-change/",
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
)
def confirm_account(
   token: str, new_email: str, db: Session = Depends(get_db)
):
    print(token, new_email)
    return {"message": "Email updated successfully!"}