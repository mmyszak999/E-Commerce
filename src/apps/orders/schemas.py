from typing import Optional

from pydantic import BaseModel

from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserInfoOutputSchema


class CartItemBaseSchema(BaseModel):
    quantity: int


class CartItemInputSchema(CartItemBaseSchema):
    product_id: str


class CartItemUpdateSchema(BaseModel):
    quantity: Optional[int]


class CartItemOutputSchema(CartItemBaseSchema):
    id: str
    product: ProductOutputSchema
    cart_item_price: float


class CartOutputSchema(BaseModel):
    id: str
    user: UserInfoOutputSchema
    user_id: str
    cart_items: list[CartItemOutputSchema]
    cart_total_price: float
    
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
