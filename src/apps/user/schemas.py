import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class UserLoginInputSchema(BaseModel):
    email: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=40)


class UserBaseSchema(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=75)
    email: str = Field(max_length=50)
    birth_date: datetime.date
    username: str = Field(max_length=50)

    class Config:
        orm_mode = True

    @validator("birth_date")
    def validate_birth_date(cls, birth_date: datetime.date) -> datetime.date:
        if birth_date >= datetime.date.today():
            raise ValueError("Birth date must be in the past")
        return birth_date


class UserRegisterSchema(UserBaseSchema):
    password: str = Field(min_length=8, max_length=40)
    password_repeat: str = Field(min_length=8, max_length=40)

    @validator("password_repeat")
    def validate_passwords(cls, rep_password: str, values: dict[str, Any]) -> str:
        if rep_password != values["password"]:
            raise ValueError("Passwords are not identical")
        return rep_password


class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[datetime.date] = None
    username: Optional[str] = None

    class Config:
        orm_mode = True


class UserInfoOutputSchema(UserBaseSchema):
    id: int
    is_active: bool = True
    

    class Config:
        orm_mode = True


class UserOutputSchema(UserBaseSchema):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    is_staff: bool = False

    class Config:
        orm_mode = True
