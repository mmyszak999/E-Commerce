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


class Cart(Base):
    __tablename__ = "cart"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    user_id = Column(
        String,
        ForeignKey("user.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    )
    cart_total_price = Column(DECIMAL, nullable=False, default=0)
    user = relationship("User", back_populates="carts")
    cart_items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_item"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    cart_id = Column(
        String,
        ForeignKey("cart.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    )
    cart = relationship("Cart", back_populates="cart_items")
    product_id = Column(
        String,
        ForeignKey("product.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    )
    product = relationship("Product", back_populates="cart_items")
    quantity = Column(Integer, nullable=False, default=1)
    cart_item_price = Column(DECIMAL, nullable=False)
    cart_item_validity = Column(
        DateTime, nullable=False, default=set_cart_item_validity
    )


class Order(Base):
    __tablename__ = "order"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    user_id = Column(
        String,
        ForeignKey("user.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    )
    user = relationship("User", back_populates="orders")
    payment = relationship(
        "Payment", uselist=False, back_populates="order"
    )
    waiting_for_payment = Column(Boolean, nullable=False, server_default="true")
    order_accepted = Column(Boolean, nullable=False, server_default="false")
    payment_accepted = Column(Boolean, nullable=False, server_default="false")
    being_delivered = Column(Boolean, nullable=False, server_default="false")
    received = Column(Boolean, nullable=False, server_default="false")
    cancelled = Column(Boolean, nullable=False, server_default="false")
    order_items = relationship("OrderItem", back_populates="order")
    total_order_price = Column(DECIMAL, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=get_current_time)
    payment_deadline = Column(DateTime, nullable=False, default=set_payment_deadline)


class OrderItem(Base):
    __tablename__ = "order_item"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    order_id = Column(
        String,
        ForeignKey("order.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    )
    order = relationship("Order", back_populates="order_items")
    product_id = Column(
        String,
        ForeignKey("product.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    )
    product = relationship("Product", back_populates="order_items")
    quantity = Column(Integer, nullable=False, default=0)
    order_item_price = Column(DECIMAL, nullable=False, default=0)
    product_price_when_order_created = Column(DECIMAL, nullable=False)
