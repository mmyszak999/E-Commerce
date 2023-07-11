from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Table
from sqlalchemy.orm import relationship

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


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    products = relationship(
        "Product", secondary=order_product_association_table, back_populates="orders"
    )
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="cascade", onupdate="cascade")
    )
    user = relationship("User", back_populates="orders")
