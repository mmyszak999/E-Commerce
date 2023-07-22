from pydantic import BaseModel


class EmailSchema(BaseModel):
    email_subject: str
    receivers: tuple[str]
    template_name: str


class EmailUpdateSchema(BaseModel):
    email: str
    password: str
    new_email: str


class EmailConfirmationSchema(BaseModel):
    token: str


class EmailChangeConfirmationSchema(EmailConfirmationSchema):
    new_email: str