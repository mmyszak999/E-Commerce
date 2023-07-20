from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    CategoryInputSchema,
    CategoryOutputSchema,
    ProductInputSchema,
    ProductOutputSchema,
)
from src.apps.products.services.category_services import (
    create_category, delete_all_categories, delete_single_category,
    get_all_categories, get_single_category, update_single_category)
from src.apps.products.services.product_services import (create_product,
                                                         delete_all_products,
                                                         delete_single_product,
                                                         get_all_products,
                                                         get_single_product,
                                                         update_single_product)
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_permission
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

category_router = APIRouter(prefix="/categories", tags=["category"])
product_router = APIRouter(prefix="/products", tags=["product"])


@category_router.post(
    "/",
    response_model=CategoryInputSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_category(
    category: CategoryInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CategoryOutputSchema:
    check_permission(request_user)
    db_category = create_category(db, category)
    return db_category


@category_router.get(
    "/",
    response_model=PagedResponseSchema[CategoryOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_categories(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[CategoryOutputSchema]:
    check_permission(request_user)
    db_categories = get_all_categories(db, page_params)
    return db_categories


@category_router.get(
    "/{category_id}",
    dependencies=[Depends(authenticate_user)],
    response_model=CategoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_category(
    category_id: int, db: Session = Depends(get_db)
) -> CategoryOutputSchema:
    db_category = get_single_category(db, category_id)
    return db_category


@category_router.patch(
    "/{category_id}",
    response_model=CategoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_category(
    category_id: int,
    category: CategoryInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CategoryOutputSchema:
    check_permission(request_user)
    db_category = update_single_category(db, category, category_id)
    return db_category


@category_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    check_permission(request_user)
    delete_single_category(db, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@category_router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_categories(
    db: Session = Depends(get_db), request_user: User = Depends(authenticate_user)
) -> Response:
    check_permission(request_user)
    delete_all_categories(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@product_router.post(
    "/",
    response_model=ProductInputSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_product(
    product: ProductInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ProductOutputSchema:
    check_permission(request_user)
    db_product = create_product(db, product)
    return db_product


@product_router.get(
    "/",
    response_model=PagedResponseSchema[ProductOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_products(
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[ProductOutputSchema]:
    check_permission(request_user)
    db_products = get_all_products(db, page_params)
    return db_products


@product_router.get(
    "/{product_id}",
    dependencies=[Depends(authenticate_user)],
    response_model=ProductOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductOutputSchema:
    db_product = get_single_product(db, product_id)
    return db_product


@product_router.patch(
    "/{product_id}",
    response_model=ProductOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_product(
    product_id: int,
    product: ProductInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ProductOutputSchema:
    check_permission(request_user)
    db_product = update_single_product(db, product, product_id)
    return db_product


@product_router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    check_permission(request_user)
    delete_single_product(db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@product_router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_products(
    db: Session = Depends(get_db), request_user: User = Depends(authenticate_user)
) -> Response:
    check_permission(request_user)
    delete_all_products(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
