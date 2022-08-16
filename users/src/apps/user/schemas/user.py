from uuid import UUID
from pydantic import BaseModel, Field


class UserLoginInputSchema(BaseModel):
    username: str
    password: str


class UserBaseSchema(BaseModel):
    first_name : str = Field(max_length=50)
    last_name : str = Field(max_length=50)
    email : str = Field(max_length=50)
    data_of_birth : str = Field(max_length=50)


class UserRegisterSchema(UserBaseSchema):
    password: str = Field(min_length=8, max_length=40)
    password_repeat: str = Field(min_length=8, max_length=40)

    class Config:
        orm_mode = True


class UserInputSchema(UserBaseSchema):
    pass

    class Config:
        orm_mode = True


class UserOutputSchema(UserBaseSchema):
    id: UUID
    is_active: bool = True

    class Config:
        orm_mode = True
     