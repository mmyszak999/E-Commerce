from pydantic import BaseModel


class EmailSchema(BaseModel):
    email_subject: str
    receivers: tuple[str]
    template_name: str


class EmailUpdateSchema(BaseModel):
    email: str
    new_email: str


class EmailConfirmationSchema(BaseModel):
    token: str