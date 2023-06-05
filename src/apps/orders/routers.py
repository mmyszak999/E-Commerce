from fastapi import Depends, status, Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.orders.schemas import (
    OrderInputSchema,
    OrderOutputSchema
)
from src.apps.orders.services import (
    create_order,
    get_single_order,
    get_all_orders,
    update_single_order,
    delete_single_order,
    delete_all_orders
)
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user
from src.core.pagination.schemas import PagedResponseSchema, T
from src.core.pagination.models import PageParams


order_router = APIRouter(prefix="/orders", tags=["order"])


@order_router.post(
    "/", dependencies=[Depends(authenticate_user)], response_model=OrderOutputSchema, status_code=status.HTTP_201_CREATED
)
def post_order(order: OrderInputSchema, db: Session = Depends(get_db)) -> OrderOutputSchema:
    db_order = create_order(db, order)
    return db_order

@order_router.get(
    "/", response_model=PagedResponseSchema[OrderOutputSchema], dependencies=[Depends(authenticate_user)], status_code=status.HTTP_200_OK
)
def get_orders(db: Session = Depends(get_db), page_params: PageParams = Depends()) -> PagedResponseSchema[OrderOutputSchema]:
    db_orders = get_all_orders(db, page_params)
    return db_orders

@order_router.get(
    "/{order_id}", dependencies=[Depends(authenticate_user)], response_model=OrderOutputSchema, status_code=status.HTTP_200_OK
)
def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderOutputSchema:
    db_order = get_single_order(db, order_id)
    return db_order

@order_router.patch(
    "/{order_id}", dependencies=[Depends(authenticate_user)], response_model=OrderOutputSchema, status_code=status.HTTP_200_OK
)
def update_order(order_id: int, order: OrderInputSchema, db: Session = Depends(get_db)) -> OrderOutputSchema:
    db_order = update_single_order(db, order, order_id)
    return db_order

@order_router.delete("/", dependencies=[Depends(authenticate_user)], status_code=status.HTTP_204_NO_CONTENT)
def delete_orders(db: Session = Depends(get_db)) -> Response:
    delete_all_orders(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@order_router.delete("/{order_id}", dependencies=[Depends(authenticate_user)], status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)) -> Response:
    delete_single_order(db, order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
