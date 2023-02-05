from fastapi import Depends, status, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    CategoryInputSchema,
    CategoryOutputSchema,
)
from src.apps.products.services.category_services import (
    create_category,
    get_all_categories,
    get_single_category,
    update_single_category,
    delete_single_category
)
from src.apps.products.models import Category
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user



product_router = APIRouter(prefix="/category", tags=["category"])

@product_router.post(
    "/create-category", response_model=CategoryInputSchema, status_code=status.HTTP_201_CREATED
)
def post_category(category: CategoryInputSchema, db: Session = Depends(get_db)) -> CategoryOutputSchema:
    db_category = create_category(db, category)
    return db_category

@product_router.get(
    "/", response_model=list[CategoryOutputSchema], dependencies=[Depends(authenticate_user)], status_code=status.HTTP_200_OK
)
def get_categories(db: Session = Depends(get_db)) -> list[CategoryOutputSchema]:
    db_categories = get_all_categories(db)
    return db_categories

@product_router.get(
    "/{category_id}", dependencies=[Depends(authenticate_user)], response_model=CategoryOutputSchema, status_code=status.HTTP_200_OK
)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryOutputSchema:
    db_category = get_single_category(db, category_id)
    return db_category

@product_router.put(
    "/{category_id}", dependencies=[Depends(authenticate_user)], response_model=CategoryOutputSchema, status_code=status.HTTP_200_OK
)
def update_category(category_id: int, category: CategoryInputSchema, db: Session = Depends(get_db)) -> CategoryOutputSchema:
    db_category = update_single_category(db, category, category_id)
    return db_category

@product_router.delete("/{category_id}", dependencies=[Depends(authenticate_user)], status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> Response:
    delete_single_category(db, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)







