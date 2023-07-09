from pydantic_factories import ModelFactory

from src.apps.user.schemas import UserRegisterSchema


class UserRegisterSchemaFactory(ModelFactory):
    __model__ = UserRegisterSchema
