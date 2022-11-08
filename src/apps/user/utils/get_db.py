from src.apps.user.database import SessionLocal

def get_db():
    with SessionLocal() as session:
        yield session