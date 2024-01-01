from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class User(Base):
    __tablename__ = "user"

    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=75), nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String(length=50), nullable=False, unique=True)
    password = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="false")
    is_superuser = Column(Boolean, nullable=False, server_default="false")
    is_staff = Column(Boolean, nullable=False, server_default="false")
    orders = relationship("Order", back_populates="user")
