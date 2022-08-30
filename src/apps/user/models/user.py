import datetime
from uuid import UUID

from sqlalchemy import Boolean, Column, Integer, String, Date

from src.apps.user.database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=75), nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String(length=50), nullable=False, unique=True)
    password = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="true")


