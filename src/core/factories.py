from pydantic_factories import ModelFactory

from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema
from src.apps.user.schemas import UserRegisterSchema


class UserRegisterSchemaFactory(ModelFactory):
    __model__ = UserRegisterSchema


class CategoryInputSchemaFactory(ModelFactory):
    __model__ = CategoryInputSchema


class ProductInputSchemaFactory(ModelFactory):
    __model__ = ProductInputSchema
