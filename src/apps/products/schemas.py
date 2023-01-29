import datetime
from typing import Any
from decimal import Decimal

from pydantic import BaseModel, Field, validator


class CategoryBaseSchema(BaseModel):
    name: str = Field(max_length=75)


class CategoryInputSchema(CategoryBaseSchema):
    pass


class CategoryOutputSchema(CategoryBaseSchema):
    pass

    class Config:
        orm_mode = True


class ProductBaseSchema(BaseModel):
    name: str = Field(max_length=75)
    price: Decimal = Field(max_length=15)
    categories: list[CategoryOutputSchema] = []


class ProductInputSchema(ProductBaseSchema):
    pass


class ProductOutputSchema(ProductBaseSchema):
    pass

    class Config:
        orm_mode = True


class ProductAddInputSchema(BaseModel):
    count: int