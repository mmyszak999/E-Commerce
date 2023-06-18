from pydantic_factories import ModelFactory

from src.apps.user.schemas import UserRegisterSchema


class UserFactory(ModelFactory):
    __model__ = UserRegisterSchema