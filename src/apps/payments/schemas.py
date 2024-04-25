from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.apps.orders.schemas import OrderOutputSchema, UserOrderOutputSchema
from src.apps.user.schemas import UserInfoOutputSchema, UserOutputSchema


class PaymentBaseOutputSchema(BaseModel):
    id: str
    amount: Decimal
    created_at: datetime
    user: UserOutputSchema
    

class PaymentOutputSchema(PaymentBaseOutputSchema):
    stripe_charge_id: str
    order: OrderOutputSchema

    class Config:
        orm_mode = True


class UserPaymentOutputSchema(PaymentBaseOutputSchema):
    order: UserOrderOutputSchema
    
    class Config:
        orm_mode = True


class PaymentAwaitSchema(BaseModel):
    order_id: str
    
    
class PaymentConfirmationSchema(PaymentAwaitSchema):
    pass


class StripePublishableKeySchema(BaseModel):
    publishable_key: str
    

class StripeSessionSchema(BaseModel):
    session_id: str
    url: str
    

    