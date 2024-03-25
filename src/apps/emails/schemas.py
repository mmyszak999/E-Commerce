from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    email_subject: str
    receivers: tuple[EmailStr]
    template_name: str


class EmailUpdateSchema(BaseModel):
    email: EmailStr
    new_email: EmailStr
