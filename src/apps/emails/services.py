from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail
from pydantic import BaseModel, BaseSettings
from sqlalchemy import update
from sqlalchemy.orm import Session

from src.apps.emails.schemas import EmailSchema, EmailUpdateSchema
from src.apps.jwt.schemas import ConfirmationTokenSchema
from src.apps.user.models import User
from src.core.exceptions import DoesNotExist, IsOccupied, ServiceException
from src.core.utils.utils import (
    check_field_values,
    confirm_token,
    generate_confirm_token,
    if_exists,
    send_email,
)
from src.settings.email_settings import EmailSettings


def email_config(settings: BaseSettings = EmailSettings):
    return ConnectionConfig(**settings().dict())


def send_activation_email(
    email: str, session: Session, background_tasks: BackgroundTasks
) -> None:
    email_schema = EmailSchema(
        email_subject="Activate your account",
        receivers=(email,),
        template_name="account_activation_email.html",
    )
    token = generate_confirm_token([email])
    body_schema = ConfirmationTokenSchema(token=token)
    send_email(email_schema, body_schema, background_tasks, settings=email_config())


def validate_email_update_data(schema: EmailUpdateSchema, session: Session) -> None:
    if schema.email == schema.new_email:
        raise ServiceException("The current email is the same as the desired one!")

    if if_exists(User, "email", schema.new_email, session):
        raise IsOccupied(User.__name__, "email", schema.new_email)


def send_email_change_confirmation_mail(
    update_schema: EmailUpdateSchema,
    session: Session,
    token: str,
    background_tasks: BackgroundTasks,
) -> None:
    validate_email_update_data(update_schema, session)

    email_schema = EmailSchema(
        email_subject="Confirm your email update",
        receivers=(update_schema.new_email,),
        template_name="email_update.html",
    )
    body_schema = ConfirmationTokenSchema(token=token)
    send_email(email_schema, body_schema, background_tasks, settings=email_config())


def change_email_service(
    email_update_schema: EmailUpdateSchema,
    request_user_email: str,
    background_tasks: BackgroundTasks,
    session: Session,
) -> None:
    check_field_values(
        request_user_email,
        email_update_schema.email,
        "Please type your current mail address in the 'email' field!",
    )
    token = generate_confirm_token(
        [email_update_schema.email, email_update_schema.new_email]
    )
    send_email_change_confirmation_mail(
        email_update_schema,
        session,
        token,
        background_tasks,
    )


def update_email(session: Session, new_email: str, current_email: str) -> None:
    user = if_exists(User, "email", current_email, session)

    if user is None:
        raise DoesNotExist(User.__name__, "email", current_email)

    if user.email == new_email:
        raise ServiceException(
            "Email can't be updated! Desired email is the same as the current email"
        )

    statement = update(User).filter(User.email == current_email).values(email=new_email)
    session.execute(statement)
    session.commit()


def confirm_email_change_service(
    db: Session, token: str, request_user_email: str
) -> None:
    emails = confirm_token(token)
    current_email, new_email = emails[0], emails[1]
    check_field_values(
        request_user_email,
        current_email,
        "Your email is different from the email requested to be changed!",
    )

    update_email(db, new_email, current_email)
