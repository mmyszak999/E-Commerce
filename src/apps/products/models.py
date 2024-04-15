from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.core.utils.utils import (
    generate_uuid,
    get_current_time,
    set_cart_item_validity,
    set_payment_deadline,
)
from src.database.db_connection import Base

category_product_association_table = Table(
    "category_product_association_table",
    Base.metadata,
    Column(
        "category_id",
        ForeignKey("category.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    ),
    Column(
        "product_id",
        ForeignKey("product.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    ),
)


class Category(Base):
    __tablename__ = "category"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    name = Column(String(length=75), nullable=False, unique=True)
    products = relationship(
        "Product",
        secondary=category_product_association_table,
        back_populates="categories",
    )


class Product(Base):
    __tablename__ = "product"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    name = Column(String(length=75), nullable=False, unique=True)
    price = Column(DECIMAL, nullable=False)
    description = Column(String(length=300), nullable=True)
    created_at = Column(DateTime, nullable=False, default=get_current_time)
    removed_from_store = Column(Boolean, nullable=False, server_default="false")
    inventory = relationship(
        "ProductInventory", uselist=False, back_populates="product"
    )
    categories = relationship(
        "Category",
        secondary=category_product_association_table,
        back_populates="products",
    )
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class ProductInventory(Base):
    __tablename__ = "product_inventory"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    quantity = Column(Integer, nullable=False)
    quantity_for_cart_items = Column(Integer, nullable=False, default=0)
    sold = Column(Integer, nullable=False, default=0)
    product_id = Column(
        String,
        ForeignKey("product.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    )
    product = relationship("Product", back_populates="inventory")
