from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base

order_product_association_table = Table(
    "order_product_association_table",
    Base.metadata,
    Column(
        "order_id",
        ForeignKey("order.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    ),
    Column(
        "product_id",
        ForeignKey("product.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    ),
)


class Cart(Base):
    __tablename__ = "cart"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    user_id = Column(
        String,
        ForeignKey("user.id", ondelete="cascade", onupdate="cascade"),
        nullable=False
    )
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
        nullable=False
    )
    cart = relationship("Cart", back_populates="cart_items")
    product_id = Column(
        String,
        ForeignKey("product.id", ondelete="cascade", onupdate="cascade"),
        nullable=False
    )
    product = relationship("Product", back_populates="cart_items")
    quantity = Column(Integer, nullable=False, default=1)
    
    
class Order(Base):
    __tablename__ = "order"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    user_id = Column(
        String,
        ForeignKey("user.id", ondelete="cascade", onupdate="cascade"),
        nullable=False
    )
    user = relationship("User", back_populates="orders")
    products = relationship(
        "Product", secondary=order_product_association_table, back_populates="orders"
    )
    order_accepted = Column(Boolean, nullable=False, server_default="false")
    payment_accepted = Column(Boolean, nullable=False, server_default="false")
    being_delivered = Column(Boolean, nullable=False, server_default="false")
    received = Column(Boolean, nullable=False, server_default="false")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_item"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    order_id = Column(
        String,
        ForeignKey("order.id", ondelete="cascade", onupdate="cascade"),
        nullable=False
    )
    order = relationship("Order", back_populates="order_items")
    product_id = Column(
        String,
        ForeignKey("product.id", ondelete="cascade", onupdate="cascade"),
        nullable=False
    )
    product = relationship("Product", back_populates="order_items")
    quantity = Column(Integer, nullable=False, default=1)
    