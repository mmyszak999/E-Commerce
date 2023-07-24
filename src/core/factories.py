from pydantic_factories import ModelFactory

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.orders.schemas import OrderInputSchema
from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema
from src.apps.user.schemas import UserRegisterSchema


class UserRegisterSchemaFactory(ModelFactory):
    __model__ = UserRegisterSchema


class CategoryInputSchemaFactory(ModelFactory):
    __model__ = CategoryInputSchema


class ProductInputSchemaFactory(ModelFactory):
    __model__ = ProductInputSchema


class OrderInputSchemaFactory(ModelFactory):
    __model__ = OrderInputSchema


class EmailUpdateSchemaFactory(ModelFactory):
    __model__ = EmailUpdateSchema



