from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.emails.services import send_confirmation_mail_change_email
from src.apps.user.models import User
from src.apps.user.services import update_email
from src.core.permissions import check_if_staff_or_owner
from src.core.utils import check_field_values, confirm_token
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user


email_router = APIRouter(prefix="/email", tags=["emails"])


@email_router.post(
    "/confirm-email-change/",
    status_code=status.HTTP_200_OK,
)
def confirm_email_change(
   token: str, db: Session = Depends(get_db),
   auth_jwt: AuthJWT = Depends(), request_user: User = Depends(authenticate_user)
):
    emails = confirm_token(token)
    current_email, new_email = emails[0], emails[1]
    check_field_values(
        request_user.email, current_email, "Your email is different from the email requested to be changed!"
        )
    
    update_email(db, new_email, current_email)
    return {"message": "Email updated successfully!"}