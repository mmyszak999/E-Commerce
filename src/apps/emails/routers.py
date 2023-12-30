from fastapi import BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.emails.services import change_email_service, confirm_email_change_service
from src.apps.user.models import User
from src.apps.user.services import activate_account_service
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

email_router = APIRouter(prefix="/email", tags=["emails"])


@email_router.post("/change-email", status_code=status.HTTP_200_OK)
def change_email(
    email_update_schema: EmailUpdateSchema,
    background_tasks: BackgroundTasks,
    request_user: User = Depends(authenticate_user),
    db: Session = Depends(get_db),
    auth_jwt: AuthJWT = Depends(),
) -> JSONResponse:
    change_email_service(email_update_schema, request_user.email, background_tasks, db)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Email change confirmation mail has been sent to the new email address!"
        },
    )


@email_router.post(
    "/confirm-email-change/{token}",
    status_code=status.HTTP_200_OK,
)
def confirm_email_change(
    token: str,
    db: Session = Depends(get_db),
    auth_jwt: AuthJWT = Depends(),
    request_user: User = Depends(authenticate_user),
) -> JSONResponse:
    confirm_email_change_service(db, token, request_user.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Email updated successfully!"},
    )


@email_router.post(
    "/confirm-account-activation/{token}",
    status_code=status.HTTP_200_OK,
)
def confirm_account_activation(
    token: str, db: Session = Depends(get_db), auth_jwt: AuthJWT = Depends()
) -> JSONResponse:
    activate_account_service(db, token)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Account activated successfully!"},
    )
