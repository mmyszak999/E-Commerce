from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Template
from pydantic import BaseModel, BaseSettings
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.apps.emails.schemas import EmailUpdateSchema, EmailSchema, EmailChangeConfirmationSchema
from src.apps.user.models import User
from src.apps.user.services import authenticate
from src.core.exceptions import ServiceException, IsOccupied
from src.settings.email_settings import EmailSettings
from src.core.utils import if_exists


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
    
    schema = EmailSchema(
        email_subject="Confirm your email update",
        receivers=(update_schema.new_email,),
        template_name="email_update.html"
    )
    body_schema = EmailChangeConfirmationSchema(token=token, new_email=update_schema.new_email)
    send_email(schema, body_schema, background_tasks)