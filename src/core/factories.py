from pydantic_factories import ModelFactory

from src.apps.user.schemas import UserRegisterSchema
from src.apps.orders.schemas import OrderInputSchema


class UserFactory(ModelFactory):
    __model__ = UserRegisterSchema


class OrderFactory(ModelFactory):
    __model__ = OrderInputSchema
    