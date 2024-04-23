from sqlalchemy import DECIMAL, Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from src.core.utils.utils import (
    generate_uuid,
    get_current_time,
    set_cart_item_validity,
    set_payment_deadline,
)
from src.database.db_connection import Base

class Payment(Base):
    __tablename__ = "payment"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    stripe_charge_id = Column(String(length=300), nullable=False)
    amount = Column(DECIMAL, nullable=False)
    user_id = Column(
        String,
        ForeignKey("user.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True
    )
    user = relationship("User", back_populates="payments")
    order_id = Column(
        String,
        ForeignKey("order.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    order = relationship("Order", back_populates="payment")
    created_at = Column(DateTime, nullable=False, default=get_current_time)