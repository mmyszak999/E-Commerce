from typing import Optional

from pydantic import BaseModel

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
