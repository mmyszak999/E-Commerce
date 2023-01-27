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


class CategoryListOutputSchema(BaseModel):
    categories: list[CategoryOutputSchema] = []


class ProductBaseSchema(BaseModel):
    name: str = Field(max_length=75)
    price: Decimal = Field(max_length=15)
    categories: CategoryListOutputSchema


class ProductInputSchema(ProductBaseSchema):
    pass


class ProductOutputSchema(ProductBaseSchema):
    pass


class ProductAddInputSchema(BaseModel):
    count: int




