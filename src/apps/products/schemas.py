import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field, validator

from src.apps.products.models import Category, Product


class CategoryBaseSchema(BaseModel):
    name: str = Field(max_length=75)


class CategoryInputSchema(CategoryBaseSchema):
    pass


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(max_length=75)


class CategoryOutputSchema(CategoryBaseSchema):
    id: int

    class Config:
        orm_mode = True


class ProductBaseSchema(BaseModel):
    name: str = Field(max_length=75)
    price: Decimal


class ProductInputSchema(ProductBaseSchema):
    category_ids: Optional[list[int]] = []


class ProductOutputSchema(ProductBaseSchema):
    id: int
    categories: list[CategoryOutputSchema] = []

    class Config:
        orm_mode = True
