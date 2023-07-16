from fastapi import Depends, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.orders.schemas import (OrderInputSchema, OrderOutputSchema,
                                     OrderUpdateSchema)
from src.apps.orders.services import (create_order, delete_all_orders,
                                      delete_single_order, get_all_orders,
                                      get_single_order, update_single_order)
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_permission, check_object_permission
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

order_router = APIRouter(prefix="/orders", tags=["order"])


@order_router.post(
    "/",
    dependencies=[Depends(authenticate_user)],
    response_model=OrderOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_order(
    order: OrderInputSchema, db: Session = Depends(get_db)
) -> OrderOutputSchema:
    db_order = create_order(db, order)
    return db_order


@order_router.get(
    "/",
    response_model=PagedResponseSchema[OrderOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_orders(
    db: Session = Depends(get_db), page_params: PageParams = Depends(), request_user: User = Depends(authenticate_user)
) -> PagedResponseSchema[OrderOutputSchema]:
    check_permission(request_user)
    db_orders = get_all_orders(db, page_params)
    return db_orders


@order_router.get(
    "/{order_id}",
    response_model=OrderOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_order(order_id: int, db: Session = Depends(get_db), request_user: User = Depends(authenticate_user)) -> OrderOutputSchema:
    db_order = get_single_order(db, order_id)
    check_object_permission(user_id=db_order.user.id, request_user=request_user)
    return db_order


@order_router.patch(
    "/{order_id}",
    response_model=OrderOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_order(
    order_id: int, order: OrderUpdateSchema, db: Session = Depends(get_db), request_user: User = Depends(authenticate_user)
) -> OrderOutputSchema:
    order_check = get_single_order(db, order_id)
    check_object_permission(user_id=order_check.user.id, request_user=request_user)
    db_order = update_single_order(db, order, order_id)
    return db_order


@order_router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_orders(db: Session = Depends(get_db), request_user: User = Depends(authenticate_user)) -> Response:
    check_permission(request_user)
    delete_all_orders(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@order_router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_order(order_id: int, db: Session = Depends(get_db), request_user: User = Depends(authenticate_user)) -> Response:
    check_permission(request_user)
    delete_single_order(db, order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
