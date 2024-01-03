from abc import abstractmethod
from datetime import datetime

from src.apps.emails.schemas import EmailUpdateSchema
from src.apps.orders.schemas import OrderInputSchema
from src.apps.products.schemas import CategoryInputSchema, ProductInputSchema, InventoryInputSchema
from src.apps.user.schemas import UserRegisterSchema, AddressInputSchema
from src.core.utils.utils import initialize_faker


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
        first_name: str = None,
        last_name: str = None,
        username: str = None,
        birth_date: datetime = None,
        password: str = "password",
        password_repeat: str = "password",
    ):
        return self.schema_class(
            first_name=first_name or self.faker.first_name(),
            last_name=last_name or self.faker.last_name(),
            email=email or self.faker.ascii_email(),
            birth_date=birth_date or self.faker.date_of_birth(),
            username=username or self.faker.user_name(),
            password=password,
            password_repeat=password_repeat,
        )


class AddressInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=AddressInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        country: str = None,
        state: str = None,
        city: str = None,
        postal_code: str = None,
        street: str = None,
        house_number: str = None,
        apartment_number: str = None,
    ):
        return self.schema_class(
            country=country or self.faker.country(),
            state=state or self.faker.state(),
            city=city or self.faker.city(),
            postal_code=postal_code or self.faker.postcode(),
            street=street or self.faker.street_name(),
            house_number=house_number or self.faker.building_number(),
            apartment_number=apartment_number or self.faker.self.faker.building_number(),
        )


class CategoryInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=CategoryInputSchema):
        super().__init__(schema_class)

    def generate(self, name: str = None):
        return self.schema_class(
            name=name or self.faker.ecommerce_category(),
        )


class InventoryInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=InventoryInputSchema):
        super().__init__(schema_class)

    def generate(
        self, quantity: int = None,
    ):
        return self.schema_class(
            quantity=quantity or self.faker.random_int(min=1)
        )


class ProductInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=ProductInputSchema):
        super().__init__(schema_class)

    def generate(
        self,
        inventory_id: str,
        name: str = None,
        price: str = None,
        description: str = None,
        category_ids: list[str] = [],
    ):
        return self.schema_class(
            inventory_id=inventory_id
            name=name or self.faker.ecommerce_name(),
            price=price or self.faker.ecommerce_price(),
            description=description or self.faker.sentence(),
            category_ids=category_ids,
        )


class OrderInputSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=OrderInputSchema):
        super().__init__(schema_class)

    def generate(self, product_ids: list[str] = []):
        return self.schema_class(product_ids=product_ids)


class EmailUpdateSchemaFactory(SchemaFactory):
    def __init__(self, schema_class=EmailUpdateSchema):
        super().__init__(schema_class)

    def generate(
        self, email: str = "default@mail.com", new_email: str = "new@mail.com"
    ):
        return self.schema_class(
            email=email,
            new_email=new_email,
        )

