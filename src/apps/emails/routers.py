from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.emails.services import send_confirmation_mail_change_email
from src.apps.emails.schemas import EmailChangeConfirmationSchema
from src.apps.user.services import update_email
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user


email_router = APIRouter(prefix="/email", tags=["emails"])


@email_router.post(
    "/confirm-email-change/",
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_200_OK,
)
def confirm_email_change(
   token: str, new_email: str, db: Session = Depends(get_db), auth_jwt: AuthJWT = Depends()
):
    update_email(db, token, new_email, auth_jwt)
    
    return {"message": "Email updated successfully!"}