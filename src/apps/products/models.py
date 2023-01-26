from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from src.database.db_connection import Base


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(length=75), nullable=False)
    products = relationship("Product")


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(length=75), nullable=False)
    price = Column(Numeric, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"))