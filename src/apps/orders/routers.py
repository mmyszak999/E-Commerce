from fastapi import Depends, Response, status, Request
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.orders.schemas import (
    OrderInputSchema,
    OrderOutputSchema,
    OrderUpdateSchema,
)
from src.apps.orders.services import (
    create_order,
    delete_single_order,
    get_all_orders,
    get_all_user_orders,
    get_single_order,
    update_single_order,
)
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema, T
from src.core.utils import check_if_request_user
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

order_router = APIRouter(prefix="/orders", tags=["order"])


@order_router.post(
    "/",
    response_model=OrderOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_order(
    order: OrderInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> OrderOutputSchema:
    return create_order(db, order, user_id=request_user.id)


@order_router.get(
    "/",
    response_model=PagedResponseSchema[OrderOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_user_orders(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[OrderOutputSchema]:
    return get_all_user_orders(db, request_user.id, page_params, request.query_params.multi_items())


@order_router.get(
    "/{order_id}",
    response_model=OrderOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> OrderOutputSchema:
    return get_single_order(db, order_id, user_id=request_user.id)


@order_router.patch(
    "/{order_id}",
    response_model=OrderOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_order(
    order_id: int,
    order: OrderUpdateSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> OrderOutputSchema:
    return update_single_order(db, order, order_id, request_user.id)


@order_router.delete(
    "/{order_id}",
    dependencies=[Depends(authenticate_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_order(order_id: int, db: Session = Depends(get_db)) -> Response:
    delete_single_order(db, order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
