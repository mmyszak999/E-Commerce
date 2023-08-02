from typing import Optional

from pydantic import BaseModel

from src.apps.products.schemas import ProductOutputSchema


class OrderBaseSchema(BaseModel):
    product_ids: list[int]


class OrderInputSchema(OrderBaseSchema):
    pass


class OrderUpdateSchema(BaseModel):
    product_ids: Optional[list[int]]


class OrderOutputSchema(BaseModel):
    id: int
    products: list[ProductOutputSchema]

    class Config:
        orm_mode = True
