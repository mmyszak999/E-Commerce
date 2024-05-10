from typing import Union

from fastapi import BackgroundTasks, Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.orders.schemas import (
    CartInputSchema,
    CartItemInputSchema,
    CartItemOutputSchema,
    CartItemUpdateSchema,
    CartOutputSchema,
    UserCartItemOutputSchema,
    UserCartOutputSchema,
    UserOrderOutputSchema,
)
from src.apps.orders.services.cart_services import (
    create_cart,
    delete_single_cart,
    get_all_carts,
    get_all_user_carts,
    get_single_cart,
)
from src.apps.orders.services.order_services import create_order
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_owner, check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

cart_router = APIRouter(prefix="/carts", tags=["cart"])


@cart_router.post(
    "/",
    response_model=UserCartOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_cart(
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> UserCartOutputSchema:
    return create_cart(db, user_id=request_user.id)


@cart_router.get(
    "/all",
    response_model=PagedResponseSchema[CartOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_carts(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[CartOutputSchema]:
    check_if_staff(request_user)
    return get_all_carts(db, page_params, request.query_params.multi_items())


@cart_router.get(
    "/",
    response_model=PagedResponseSchema[UserCartOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_logged_user_cart(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[UserCartOutputSchema]:
    return get_all_user_carts(
        db, request_user.id, page_params, request.query_params.multi_items()
    )


@cart_router.get(
    "/{cart_id}",
    response_model=Union[CartOutputSchema, UserCartOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_cart(
    cart_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[CartOutputSchema, UserCartOutputSchema]:
    db_cart = get_single_cart(db, cart_id)
    if check_if_staff_or_owner(request_user, "id", db_cart.user_id):
        if request_user.is_staff:
            return get_single_cart(db, cart_id, as_staff=True)
        return get_single_cart(db, cart_id)


@cart_router.delete(
    "/{cart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_cart(
    cart_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    check_if_staff(request_user)
    delete_single_cart(db, cart_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@cart_router.post(
    "/{cart_id}/order",
    response_model=UserOrderOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_order_from_cart(
    cart_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> UserOrderOutputSchema:
    db_cart = get_single_cart(db, cart_id)
    check_if_staff_or_owner(request_user, "id", db_cart.user_id)
    return create_order(db, request_user.id, cart_id, background_tasks)
