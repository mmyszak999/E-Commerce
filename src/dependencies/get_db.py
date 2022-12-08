from src.database.db_connection import SessionLocal

def get_db():
    with SessionLocal() as session:
        yield session