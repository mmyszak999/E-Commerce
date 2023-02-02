from fastapi import Depends, status, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    CategoryInputSchema,
    CategoryOutputSchema,
)
from src.apps.products.services.category_services import (
    create_category
)
from src.apps.products.models import Category
from src.dependencies.get_db import get_db


product_router = APIRouter(prefix="/category", tags=["category"])

@product_router.post("/create-category", response_model=CategoryInputSchema, status_code=status.HTTP_201_CREATED)
def create_user(category: CategoryInputSchema, db: Session = Depends(get_db)) -> CategoryOutputSchema:
    db_category = create_category(db, category)
    return db_category