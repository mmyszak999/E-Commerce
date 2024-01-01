import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, Table
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


class Order(Base):
    __tablename__ = "order"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    products = relationship(
        "Product", secondary=order_product_association_table, back_populates="orders"
    )
    user_id = Column(
        String,
        ForeignKey("user.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
        default=generate_uuid,
    )
    user = relationship("User", back_populates="orders")
