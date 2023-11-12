from fastapi import BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.emails.services import (
    confirm_email_change_service,
    send_confirmation_mail_change_email,
)
from src.apps.user.models import User
from src.core.utils import check_field_values, generate_confirm_token
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

email_router = APIRouter(prefix="/email", tags=["emails"])


@email_router.post(
    "/change-email",
    status_code=status.HTTP_200_OK
)
def change_email(
    email_update_schema: EmailUpdateSchema, background_tasks: BackgroundTasks, request_user: User = Depends(authenticate_user),
    db: Session = Depends(get_db), auth_jwt: AuthJWT = Depends()
) -> JSONResponse:
    check_field_values(
        request_user.email, email_update_schema.email, "Please type your current mail address in the 'email' field!"
    )
    token = generate_confirm_token([email_update_schema.email, email_update_schema.new_email])
    send_confirmation_mail_change_email(
        email_update_schema,
        db,
        token,
        background_tasks,
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Email change confirmation mail has been sent to the new email address!"}
    )


@email_router.post(
    "/confirm-email-change/{token}",
    status_code=status.HTTP_200_OK,
)
def confirm_email_change(
   token: str, db: Session = Depends(get_db),
   auth_jwt: AuthJWT = Depends(), request_user: User = Depends(authenticate_user)
) -> JSONResponse:
    confirm_email_change_service(db, token, request_user.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Email updated successfully!"}
    )
    