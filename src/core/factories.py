from pydantic_factories import ModelFactory

from src.apps.user.schemas import UserRegisterSchema
from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema


class UserRegisterSchemaFactory(ModelFactory):
    __model__ = UserRegisterSchema


class CategoryFactory(ModelFactory):
    __model__ = CategoryInputSchema
   
    
class ProductFactory(ModelFactory):
    __model__ = ProductInputSchema
