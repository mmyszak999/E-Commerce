import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field, validator

from src.apps.orders.models import Order
from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema


class OrderBaseSchema(BaseModel):
    product_ids: list[int] = []
    user_id: int


class OrderInputSchema(OrderBaseSchema):
    pass


class OrderUpdateSchema(BaseModel):
    product_ids: Optional[list[int]] = []
    user_id: Optional[int]


class OrderOutputSchema(BaseModel):
    id: int
    products: list[ProductOutputSchema]
    user: UserOutputSchema

    class Config:
        orm_mode = True
