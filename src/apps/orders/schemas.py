import datetime
from typing import Any, Optional
from decimal import Decimal

from pydantic import BaseModel, Field, validator

from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.apps.orders.models import Order


class OrderBaseSchema(BaseModel):
    product_ids: Optional[list[int]] = []
    user_id: Optional[int]
    
    
class OrderInputSchema(OrderBaseSchema):
    pass


class OrderOutputSchema(BaseModel):
    id: int
    products: list[ProductOutputSchema]
    user: UserOutputSchema
    
    class Config:
        orm_mode = True
    