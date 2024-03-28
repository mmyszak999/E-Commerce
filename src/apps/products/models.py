from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base

category_product_association_table = Table(
    "category_product_association_table",
    Base.metadata,
    Column(
        "category_id",
        ForeignKey("category.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
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
