from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship

from src.database.db_connection import Base
from src.apps.orders.models import order_product_association_table


category_product_association_table = Table(
    "category_product_association_table",
    Base.metadata,
    Column("category_id", ForeignKey("category.id", ondelete='cascade', onupdate='cascade'), nullable=False),
    Column("product_id", ForeignKey("product.id", ondelete='cascade', onupdate='cascade'), nullable=False),
)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(length=75), nullable=False, unique=True)
    products = relationship("Product", secondary=category_product_association_table, back_populates="categories")


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(length=75), nullable=False, unique=True)
    price = Column(Numeric, nullable=False)
    categories = relationship("Category", secondary=category_product_association_table, back_populates="products")
    orders = relationship("Order", secondary=order_product_association_table, back_populates='products')