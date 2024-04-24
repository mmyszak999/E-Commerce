from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    InventoryOutputSchema,
    ProductInputSchema,
    ProductOutputSchema,
    ProductUpdateSchema,
    ProductWithoutInventoryOutputSchema,
    RemovedProductOutputSchema,
)
from src.apps.products.services.inventory_services import get_single_inventory
from src.apps.products.services.product_services import (
    create_product,
    get_all_available_products,
    get_all_products,
    get_available_single_product,
    get_single_product_or_inventory,
    remove_single_product_from_store,
    update_single_product,
)
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

product_router = APIRouter(prefix="/products", tags=["product"])


@product_router.post(
    "/",
    response_model=ProductOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_product(
    product: ProductInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ProductOutputSchema:
    check_if_staff(request_user)
    return create_product(db, product)


@product_router.get(
    "/",
    response_model=PagedResponseSchema[ProductWithoutInventoryOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_available_products(
    request: Request, db: Session = Depends(get_db), page_params: PageParams = Depends()
) -> PagedResponseSchema[ProductWithoutInventoryOutputSchema]:
    return get_all_available_products(
        db, page_params, query_params=request.query_params.multi_items()
    )


@product_router.get(
    "/all",
    response_model=PagedResponseSchema[ProductOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_products(
    request: Request,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[ProductOutputSchema]:
    check_if_staff(request_user)
    print(request.__dict__, "ww")
    return get_all_products(db, page_params, request.query_params.multi_items())


@product_router.get(
    "/all/{product_id}",
    response_model=ProductOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_product_as_staff(
    product_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ProductOutputSchema:
    check_if_staff(request_user)
    return get_single_product_or_inventory(db, product_id)


@product_router.get(
    "/{product_id}",
    response_model=Union[
        ProductWithoutInventoryOutputSchema, RemovedProductOutputSchema
    ],
    status_code=status.HTTP_200_OK,
)
def get_product(
    product_id: str, db: Session = Depends(get_db)
) -> Union[ProductWithoutInventoryOutputSchema, RemovedProductOutputSchema]:
    return get_available_single_product(db, product_id)


@product_router.get(
    "/{product_id}/inventory",
    response_model=InventoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_product_inventory(
    product_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> InventoryOutputSchema:
    check_if_staff(request_user)
    return get_single_product_or_inventory(db, product_id, get_inventory=True)


@product_router.patch(
    "/{product_id}",
    response_model=ProductOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_product(
    product_id: str,
    product: ProductUpdateSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ProductOutputSchema:
    check_if_staff(request_user)
    return update_single_product(db, product, product_id)


@product_router.patch(
    "/{product_id}/remove",
    status_code=status.HTTP_200_OK,
)
def remove_product_from_store(
    product_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    check_if_staff(request_user)
    result = remove_single_product_from_store(db, product_id)
    return JSONResponse(result)
