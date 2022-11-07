from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.settings.db_settings import settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///./src/apps/user/sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    url=settings.postgres_url, echo=True
    )

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
    )

Base = declarative_base()
