import datetime
from typing import Any
from decimal import Decimal

from pydantic import BaseModel, Field, validator

from src.apps.products.models import Category, Product


class CategoryBaseSchema(BaseModel):
    name: str = Field(max_length=75)


class CategoryInputSchema(CategoryBaseSchema):
    pass


class CategoryOutputSchema(CategoryBaseSchema):
    id: int

    class Config:
        orm_mode = True


class ProductBaseSchema(BaseModel):
    name: str = Field(max_length=75)
    price: Decimal


class ProductInputSchema(ProductBaseSchema):
    categories_ids: list[int] = []


class ProductOutputSchema(ProductBaseSchema):
    id: int    
    categories: list[CategoryOutputSchema] = []


    class Config:
        orm_mode = True
