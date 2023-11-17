from datetime import datetime
from random import Random

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.orders.schemas import OrderInputSchema
from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema
from src.apps.user.schemas import UserRegisterSchema
from src.core.utils import initialize_faker


def generate_user_register_schema(
    email: str = None,
    username: str = None,
    birth_date: datetime = None,
    password: str = "password",
    password_repeat: str = "password",
):
    faker = initialize_faker()
    return UserRegisterSchema(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=email or faker.ascii_email(),
        birth_date=birth_date or faker.date_of_birth(),
        username=username or faker.user_name(),
        password=password,
        password_repeat=password_repeat,
    )


class CategoryInputSchemaFactory(ModelFactory):
    __model__ = CategoryInputSchema
    __random__ = Random(10)


class ProductInputSchemaFactory(ModelFactory):
    __model__ = ProductInputSchema
    __random__ = Random(10)


class OrderInputSchemaFactory(ModelFactory):
    __model__ = OrderInputSchema
    __random__ = Random(10)


class EmailUpdateSchemaFactory(ModelFactory):
    __model__ = EmailUpdateSchema
