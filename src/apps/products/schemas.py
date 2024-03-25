from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator


class CategoryBaseSchema(BaseModel):
    name: str = Field(max_length=75)


class CategoryInputSchema(CategoryBaseSchema):
    pass


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(max_length=75)


class CategoryOutputSchema(CategoryBaseSchema):
    id: str

    class Config:
        orm_mode = True


class InventoryBaseSchema(BaseModel):
    quantity: int

    @validator("quantity")
    def validate_quantity(cls, quantity: int) -> str:
        if quantity < 0:
            raise ValueError("Quantity of a product must be a positive integer!")
        return quantity


class InventoryInputSchema(InventoryBaseSchema):
    pass


class InventoryUpdateSchema(BaseModel):
    quantity: Optional[int]

    @validator("quantity")
    def validate_quantity(cls, quantity: int) -> str:
        if quantity < 0:
            raise ValueError("Quantity of a product must be a positive integer!")
        return quantity


class InventoryOutputSchema(InventoryBaseSchema):
    id: str
    quantity_for_cart_items: int
    sold: int

    class Config:
        orm_mode = True


class ProductBaseSchema(BaseModel):
    name: str = Field(max_length=75)
    price: Decimal
    description: str


class ProductInputSchema(ProductBaseSchema):
    category_ids: list[str]
    inventory: InventoryInputSchema


class ProductUpdateSchema(ProductBaseSchema):
    name: Optional[str]
    price: Optional[Decimal]
    description: Optional[str]
    category_ids: Optional[list[str]]
    inventory: Optional[InventoryUpdateSchema]


class ProductOutputSchema(ProductBaseSchema):
    id: str
    categories: list[CategoryOutputSchema]
    inventory: InventoryOutputSchema

    class Config:
        orm_mode = True
