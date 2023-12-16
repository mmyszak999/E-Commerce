from abc import abstractmethod
from datetime import datetime
from random import Random

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.orders.schemas import OrderInputSchema
from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema
from src.apps.user.schemas import UserRegisterSchema
from src.core.utils import initialize_faker


class SchemaFactory:
    def __init__(self, schema_class):
        self.schema_class = schema_class
        self.faker = initialize_faker()
    
    @abstractmethod
    def generate(self, **kwargs):
        raise NotImplementedError()
    

class UserRegisterSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=UserRegisterSchema):
        super().__init__(schema_class)
    
    def generate(
        self,
        email: str = None,
        username: str = None,
        birth_date: datetime = None,
        password: str = "password",
        password_repeat: str = "password",
    ):
        return self.schema_class(
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
            email=email or self.faker.ascii_email(),
            birth_date=birth_date or self.faker.date_of_birth(),
            username=username or self.faker.user_name(),
            password=password,
            password_repeat=password_repeat,
        )
    

"""def generate_user_register_schema(
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
    )"""

class CategoryInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=CategoryInputSchema):
        super().__init__(schema_class)
    
    def generate(self, category_name: str = None):
        return self.schema_class(
            name=category_name or self.faker.ecommerce_category(),
        )


class ProductInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ProductInputSchema):
        super().__init__(schema_class)
    
    def generate(
        self,
        product_name: str = None,
        price: str = None,
        category_ids: list[int] = []
    ):
        return self.schema_class(
            name=product_name or self.faker.ecommerce_name(),
            price=price or self.faker.ecommerce_price(),
            category_ids=category_ids
        )


class OrderInputSchemaFactory(ModelFactory):
    __model__ = OrderInputSchema
    __random__ = Random(10)


class EmailUpdateSchemaFactory(ModelFactory):
    __model__ = EmailUpdateSchema
