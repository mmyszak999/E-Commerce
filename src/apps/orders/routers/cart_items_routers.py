from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.orders.routers.cart_routers import cart_router
from src.apps.orders.schemas import (
    CartInputSchema,
    CartItemInputSchema,
    CartItemOutputSchema,
    CartItemUpdateSchema,
    CartOutputSchema,
    UserCartItemOutputSchema
)
from src.apps.orders.services.cart_items_services import (
    create_cart_item,
    delete_single_cart_item,
    get_all_cart_items_for_single_cart,
    get_single_cart_item,
    update_cart_item,
)
from src.apps.orders.services.cart_services import get_single_cart
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner, check_if_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

cart_items_router = APIRouter(prefix="/carts/{cart_id}/items", tags=["cart-items"])


@cart_items_router.post(
    "/",
    response_model=UserCartItemOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_cart_item(
    cart_id: str,
    cart_item: CartItemInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> UserCartItemOutputSchema:
    cart_check = get_single_cart(db, cart_id)
    check_if_staff_or_owner(request_user, "id", cart_check.user_id)
    return create_cart_item(db, cart_item, cart_id)


@cart_items_router.get(
    "/{cart_item_id}",
    response_model=Union[CartItemOutputSchema, UserCartItemOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_cart_item(
    cart_id: str,
    cart_item_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[CartItemOutputSchema, UserCartItemOutputSchema]:
    db_cart = get_single_cart(db, cart_id)
    if check_if_staff_or_owner(request_user, "id", db_cart.user_id):
        if request_user.is_staff: 
            return get_single_cart_item(db, cart_item_id, as_staff=True) 
        return get_single_cart_item(db, cart_item_id)


@cart_items_router.get(
    "/",
    response_model=Union[
        PagedResponseSchema[CartItemOutputSchema],
        PagedResponseSchema[UserCartItemOutputSchema]
    ],
    status_code=status.HTTP_200_OK,
)
def get_cart_items_for_single_cart(
    request: Request,
    cart_id: str,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
        PagedResponseSchema[CartItemOutputSchema],
        PagedResponseSchema[UserCartItemOutputSchema]
    ]:
    db_cart = get_single_cart(db, cart_id)
    if check_if_staff_or_owner(request_user, "id", db_cart.user_id):
        if request_user.is_staff: 
            return get_all_cart_items_for_single_cart(
            db, cart_id, page_params, request.query_params.multi_items(), as_staff=True
            )
        return get_all_cart_items_for_single_cart(
            db, cart_id, page_params, request.query_params.multi_items()
            )


@cart_items_router.patch(
    "/{cart_item_id}",
    response_model=UserCartItemOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_single_cart_item(
    cart_id: str,
    cart_item_id: str,
    cart_item_input: CartItemUpdateSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> UserCartItemOutputSchema:
    cart_check = get_single_cart(db, cart_id)
    check_if_staff_or_owner(request_user, "id", cart_check.user_id)
    return update_cart_item(db, cart_item_input, cart_item_id, cart_id)


@cart_items_router.delete(
    "/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_cart_item(
    cart_id: str,
    cart_item_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    cart_check = get_single_cart(db, cart_id)
    check_if_staff_or_owner(request_user, "id", cart_check.user_id)
    delete_single_cart_item(db, cart_id, cart_item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
