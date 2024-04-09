from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, Any

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
    cart_item_validity: Any

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


class OrderItemOutputSchema(BaseModel):
    id: str
    order_id: str
    product: ProductOutputSchema
    quantity: int
    order_item_price: Decimal
    
    class Config:
        orm_mode = True
    

class OrderOutputSchema(BaseModel):
    id: str
    user_id: str
    waiting_for_payment: bool
    order_accepted: bool
    payment_accepted: bool
    being_delivered: bool
    received: bool
    cancelled: bool
    order_items: list[OrderItemOutputSchema]
    total_order_price: Decimal
    created_at: datetime
    payment_deadline: datetime

    class Config:
        orm_mode = True
