from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import BaseModel, BaseSettings
from sqlalchemy import update
from sqlalchemy.orm import Session

from src.apps.emails.schemas import EmailSchema, EmailUpdateSchema
from src.apps.jwt.schemas import ConfirmationTokenSchema
from src.apps.user.models import User
from src.core.exceptions import DoesNotExist, IsOccupied, ServiceException
from src.core.utils import check_field_values, confirm_token, if_exists
from src.settings.email_settings import EmailSettings


def email_config(settings: BaseSettings = EmailSettings):
    return ConnectionConfig(**settings().dict())


def validate_email_update_data(schema: EmailUpdateSchema, session: Session) -> None:
    if schema.email == schema.new_email:
        raise ServiceException("The current email is the same as the desired one!")
    
    if if_exists(User, "email", schema.new_email, session):
        raise IsOccupied(User.__name__, "email", schema.new_email)
    

def send_email(schema: EmailSchema, body_schema: BaseModel, background_tasks: BackgroundTasks) -> None:
    email_message = MessageSchema(
        subject=schema.email_subject,
        recipients=schema.receivers,
        template_body=body_schema.dict(),
        subtype='html'
    )
    
    fast_mail = FastMail(email_config())
    background_tasks.add_task(
        fast_mail.send_message,
        email_message,
        template_name=schema.template_name
    )


def send_confirmation_mail_change_email(
    update_schema: EmailUpdateSchema, session: Session,
    token: str, background_tasks: BackgroundTasks) -> None:
    validate_email_update_data(update_schema, session)
    
    email_schema = EmailSchema(
        email_subject="Confirm your email update",
        receivers=(update_schema.new_email,),
        template_name="email_update.html"
    )
    body_schema = ConfirmationTokenSchema(token=token)
    send_email(email_schema, body_schema, background_tasks)
    
    
def update_email(
    session: Session, new_email: str, current_email: str
) -> None:
    user = if_exists(User, "email", current_email, session)

    if user is None:
        raise DoesNotExist(User.__name__, "email", current_email)
    
    if user.email == new_email:
        raise ServiceException("Email cant't be updated! Desired email is the same as the current email")

    statement = update(User).filter(User.email == current_email).values(email=new_email)
    session.execute(statement)
    session.commit()


def confirm_email_change_service(db: Session, token: str, request_user_email: str) -> None:
    emails = confirm_token(token)
    current_email, new_email = emails[0], emails[1]
    check_field_values(
        request_user_email, current_email, "Your email is different from the email requested to be changed!"
        )
    
    update_email(db, new_email, current_email)