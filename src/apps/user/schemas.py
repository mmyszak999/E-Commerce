import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class AddressBaseSchema(BaseModel):
    country: str
    state: str
    city: str
    postal_code: str
    street: str = ""
    house_number: str
    apartment_number: str = ""


class AddressInputSchema(AddressBaseSchema):
    pass

    class Config:
        orm_mode = True


class AddressUpdateSchema(BaseModel):
    country: Optional[str]
    state: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    street: Optional[str]
    house_number: Optional[str]
    apartment_number: Optional[str]


class AddressOutputSchema(AddressBaseSchema):
    id: str

    class Config:
        orm_mode = True


class UserLoginInputSchema(BaseModel):
    email: EmailStr = Field()
    password: str = Field(min_length=8, max_length=40)


class UserBaseSchema(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=75)
    email: EmailStr = Field()
    birth_date: datetime.date
    username: str = Field(max_length=50)
    address: AddressInputSchema

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
    first_name: Optional[str]
    last_name: Optional[str]
    birth_date: Optional[datetime.date]
    username: Optional[str]
    address: Optional[AddressUpdateSchema]

    class Config:
        orm_mode = True


class UserInfoOutputSchema(BaseModel):
    username: str
    is_active: bool

    class Config:
        orm_mode = True


class UserOutputSchema(UserBaseSchema):
    id: str
    is_active: bool
    is_superuser: bool
    is_staff: bool
    address: AddressOutputSchema

    class Config:
        orm_mode = True
