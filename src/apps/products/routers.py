from fastapi import Depends, status, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    CategoryInputSchema,
    CategoryOutputSchema,
    ProductInputSchema,
    ProductOutputSchema
)
from src.apps.products.services.category_services import (
    create_category,
    get_all_categories,
    get_single_category,
    update_single_category,
    delete_single_category,
    delete_all_categories
)
from src.apps.products.services.product_services import (
    create_product,
    get_all_products,
    get_single_product,
    update_single_product,
    delete_single_product
)
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user
from src.core.pagination.schemas import PagedResponseSchema, T
from src.core.pagination.models import PageParams


category_router = APIRouter(prefix="/categories", tags=["category"])
product_router = APIRouter(prefix="/products", tags=["product"])


@category_router.post(
    "/", dependencies=[Depends(authenticate_user)], response_model=CategoryInputSchema, status_code=status.HTTP_201_CREATED
)
def post_category(category: CategoryInputSchema, db: Session = Depends(get_db)) -> CategoryOutputSchema:
    db_category = create_category(db, category)
    return db_category

@category_router.get(
    "/", response_model=PagedResponseSchema[CategoryOutputSchema], dependencies=[Depends(authenticate_user)], status_code=status.HTTP_200_OK
)
def get_categories(db: Session = Depends(get_db), page_params: PageParams = Depends()) -> PagedResponseSchema[CategoryOutputSchema]:
    db_categories = get_all_categories(db, page_params)
    return db_categories

@category_router.get(
    "/{category_id}", dependencies=[Depends(authenticate_user)], response_model=CategoryOutputSchema, status_code=status.HTTP_200_OK
)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryOutputSchema:
    db_category = get_single_category(db, category_id)
    return db_category

@category_router.put(
    "/{category_id}", dependencies=[Depends(authenticate_user)], response_model=CategoryOutputSchema, status_code=status.HTTP_200_OK
)
def update_category(category_id: int, category: CategoryInputSchema, db: Session = Depends(get_db)) -> CategoryOutputSchema:
    db_category = update_single_category(db, category, category_id)
    return db_category

@category_router.delete("/", dependencies=[Depends(authenticate_user)], status_code=status.HTTP_204_NO_CONTENT)
def delete_categories(db: Session = Depends(get_db)) -> Response:
    delete_all_categories(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@category_router.delete("/{category_id}", dependencies=[Depends(authenticate_user)], status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> Response:
    delete_single_category(db, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@product_router.post(
    "/", dependencies=[Depends(authenticate_user)], response_model=ProductInputSchema, status_code=status.HTTP_201_CREATED
)
def post_product(product: ProductInputSchema, db: Session = Depends(get_db)) -> ProductOutputSchema:
    db_product = create_product(db, product)
    return db_product

@product_router.get(
    "/", response_model=PagedResponseSchema[ProductOutputSchema], dependencies=[Depends(authenticate_user)], status_code=status.HTTP_200_OK
)
def get_products(db: Session = Depends(get_db), page_params: PageParams = Depends()) -> PagedResponseSchema[ProductOutputSchema]:
    db_products = get_all_products(db, page_params)
    return db_products

@product_router.get(
    "/{product_id}", dependencies=[Depends(authenticate_user)], response_model=ProductOutputSchema, status_code=status.HTTP_200_OK
)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductOutputSchema:
    db_product = get_single_product(db, product_id)
    return db_product

@product_router.put(
    "/{product_id}", dependencies=[Depends(authenticate_user)], response_model=ProductOutputSchema, status_code=status.HTTP_200_OK
)
def update_product(product_id: int, product: ProductInputSchema, db: Session = Depends(get_db)) -> ProductOutputSchema:
    db_product = update_single_product(db, product, product_id)
    return db_product

@product_router.delete("/{product_id}", dependencies=[Depends(authenticate_user)], status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> Response:
    delete_single_product(db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
