from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, validator

from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserInfoOutputSchema


class CartItemBaseSchema(BaseModel):
    quantity: int
    
    @validator("quantity")
    def validate_quantity(cls, quantity: int) -> str:
        if quantity < 0:
            raise ValueError("Quantity of a product must be a positive integer!")
        return quantity


class CartItemInputSchema(CartItemBaseSchema):
    product_id: str


class CartItemUpdateSchema(BaseModel):
    quantity: Optional[int]
    
    @validator("quantity")
    def validate_quantity(cls, quantity: int) -> str:
        if quantity < 0:
            raise ValueError("Quantity of a product must be a positive integer!")
        return quantity


class CartItemOutputSchema(CartItemBaseSchema):
    id: str
    product: ProductOutputSchema
    cart_id: str
    cart_item_price: Decimal
    
    class Config:
        orm_mode = True
        

class CartBaseSchema(BaseModel):
    user_id: str


class CartInputSchema(CartBaseSchema):
    pass


class CartOutputSchema(CartBaseSchema):
    id: str
    user: UserInfoOutputSchema
    cart_items: list[CartItemOutputSchema]
    cart_total_price: Decimal
    
    class Config:
        orm_mode = True


class OrderBaseSchema(BaseModel):
    product_ids: list[str]


class OrderInputSchema(OrderBaseSchema):
    pass

    class Config:
        orm_mode = True


class OrderUpdateSchema(BaseModel):
    product_ids: Optional[list[str]]


class OrderOutputSchema(BaseModel):
    id: str
    products: list[ProductOutputSchema]

    class Config:
        orm_mode = True
