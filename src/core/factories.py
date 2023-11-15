from random import randint, Random
from datetime import datetime 
from faker import Faker
from pydantic import BaseModel
from faker.providers import person, internet, date_time, misc

from polyfactory.factories.pydantic_factory import ModelFactory

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.orders.schemas import OrderInputSchema
from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema
from src.apps.user.schemas import UserRegisterSchema

faker = Faker('en_US')
Faker.seed("")
faker.add_provider(person)
faker.add_provider(internet)
faker.add_provider(date_time)
faker.add_provider(misc)


class UserRegisterSchemaFactory(UserRegisterSchema):   
    first_name: str = faker.first_name()
    last_name: str = faker.last_name()
    email: str = faker.ascii_email()
    birth_date: datetime = faker.date_of_birth()
    username: str = faker.domain_word()
    password: str = faker.password()
    password_repeat: str = faker.password()
          

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



