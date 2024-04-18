from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.orders.schemas import OrderItemOutputSchema, UserOrderItemOutputSchema
from src.apps.orders.services.order_items_services import (
    get_all_order_items_for_single_order,
    get_single_order_item,
)
from src.apps.orders.services.order_services import get_single_order
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

order_items_router = APIRouter(prefix="/orders/{order_id}/items", tags=["order-items"])


@order_items_router.get(
    "/{order_item_id}",
    response_model=Union[
        OrderItemOutputSchema,
        UserOrderItemOutputSchema
    ],
    status_code=status.HTTP_200_OK,
)
def get_order_item(
    order_id: str,
    order_item_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[
        OrderItemOutputSchema,
        UserOrderItemOutputSchema
    ]:
    db_order = get_single_order(db, order_id)
    if check_if_staff_or_owner(request_user, "id", db_order.user_id):
        if request_user.is_staff: 
            return get_single_order_item(db, order_item_id, as_staff=True) 
        return get_single_order_item(db, order_item_id)


@order_items_router.get(
    "/",
    response_model=PagedResponseSchema[UserOrderItemOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_order_items_for_single_order(
    request: Request,
    order_id: str,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserOrderItemOutputSchema]:
    order_check = get_single_order(db, order_id)
    check_if_staff_or_owner(request_user, "id", order_check.user_id)
    return get_all_order_items_for_single_order(
        db, order_id, page_params, request.query_params.multi_items()
    )
