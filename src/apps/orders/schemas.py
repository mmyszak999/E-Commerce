from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, validator

from src.apps.products.schemas import ProductOutputSchema, ProductWithoutInventoryOutputSchema
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


class BaseCartItemOutputSchema(CartItemBaseSchema):
    id: str
    cart_id: str
    cart_item_price: Decimal
    cart_item_validity: datetime


class UserCartItemOutputSchema(BaseCartItemOutputSchema):
    product: ProductWithoutInventoryOutputSchema
    
    class Config:
        orm_mode = True


class CartItemOutputSchema(BaseCartItemOutputSchema):
    product: ProductOutputSchema
    
    class Config:
        orm_mode = True


class CartBaseSchema(BaseModel):
    user_id: str


class CartInputSchema(CartBaseSchema):
    pass


class BaseCartOutputSchema(CartBaseSchema):
    id: str
    user: UserInfoOutputSchema
    cart_total_price: Decimal
    
    class Config:
        orm_mode = True


class CartOutputSchema(BaseCartOutputSchema):
    cart_items: list[CartItemOutputSchema]
    
    class Config:
        orm_mode = True


class UserCartOutputSchema(BaseCartOutputSchema):
    cart_items: list[UserCartItemOutputSchema]
    
    class Config:
        orm_mode = True


class BaseOrderItemOutputSchema(BaseModel):
    id: str
    order_id: str
    quantity: int
    order_item_price: Decimal
    product_price_when_order_created: Decimal


class OrderItemOutputSchema(BaseOrderItemOutputSchema):
    product: ProductOutputSchema

    class Config:
        orm_mode = True
        
        
class UserOrderItemOutputSchema(BaseOrderItemOutputSchema):
    product: ProductWithoutInventoryOutputSchema

    class Config:
        orm_mode = True


class BaseOrderOutputSchema(BaseModel):
    id: str
    user_id: str
    waiting_for_payment: bool
    order_accepted: bool
    payment_accepted: bool
    being_delivered: bool
    received: bool
    cancelled: bool
    total_order_price: Decimal
    created_at: datetime
    payment_deadline: datetime
    
    
class OrderOutputSchema(BaseOrderOutputSchema):
    order_items: list[OrderItemOutputSchema]
    
    class Config:
        orm_mode = True
    
class UserOrderOutputSchema(BaseOrderOutputSchema):
    order_items: list[UserOrderItemOutputSchema]
    
    class Config:
        orm_mode = True
