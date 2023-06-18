from pydantic_factories import ModelFactory

from src.apps.user.schemas import UserRegisterSchema
from src.apps.orders.schemas import OrderInputSchema
from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema


class UserFactory(ModelFactory):
    __model__ = UserRegisterSchema


class OrderFactory(ModelFactory):
    __model__ = OrderInputSchema
    
class CategoryFactory(ModelFactory):
    __model__ = CategoryInputSchema
   
    
class ProductFactory(ModelFactory):
    __model__ = ProductInputSchema

