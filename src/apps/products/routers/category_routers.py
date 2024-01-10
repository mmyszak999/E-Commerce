from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    CategoryInputSchema,
    CategoryOutputSchema
)
from src.apps.products.services.category_services import (
    create_category,
    delete_single_category,
    get_all_categories,
    get_single_category,
    update_single_category,
)

from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

category_router = APIRouter(prefix="/categories", tags=["category"])

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
    check_if_staff(request_user)
    return create_category(db, category)


@category_router.get(
    "/",
    response_model=PagedResponseSchema[CategoryOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_categories(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[CategoryOutputSchema]:
    return get_all_categories(db, page_params, request.query_params.multi_items())


@category_router.get(
    "/{category_id}",
    response_model=CategoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_category(
    category_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CategoryOutputSchema:
    check_if_staff(request_user)
    return get_single_category(db, category_id)


@category_router.patch(
    "/{category_id}",
    response_model=CategoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_category(
    category_id: str,
    category: CategoryInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CategoryOutputSchema:
    check_if_staff(request_user)
    return update_single_category(db, category, category_id)

@category_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    check_if_staff(request_user)
    delete_single_category(db, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)