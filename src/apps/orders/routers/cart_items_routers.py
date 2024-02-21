from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.orders.schemas import (
    CartItemInputSchema,
    CartItemOutputSchema,
    CartItemUpdateSchema,
    CartOutputSchema,
    CartInputSchema
)
from src.apps.orders.services.cart_services import (
    get_single_cart
)
from src.apps.orders.services.cart_items_services import (
    create_cart_item,
    get_single_cart_item
)
from src.apps.orders.routers.cart_routers import cart_router
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff, check_if_staff_or_owner
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

cart_items_router = APIRouter(prefix="/carts/{cart_id}/items", tags=["cart-items"])

"""
    Routers that are part of cart routers, but they are linked to cart item logic
"""

@cart_items_router.post(
    "/",
    dependencies=[Depends(authenticate_user)],
    response_model=CartItemOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_cart_item(
    cart_id: str,
    cart_item: CartItemInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CartOutputSchema:
    return create_cart_item(db, cart_item, cart_id)


@cart_items_router.get(
    "/{cart_item_id}",
    response_model=CartItemOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_cart_item(
    cart_id: str,
    cart_item_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CartOutputSchema:
    cart_check = get_single_cart(db, cart_id)
    check_if_staff_or_owner(request_user, "id", cart_check.user_id)
    db_cart_item = get_single_cart_item(db, cart_item_id)
    return db_cart_item

@cart_items_router.get(
    "/ww",
    status_code=status.HTTP_200_OK,
)
def test(
    cart_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CartOutputSchema:
    return {"ww": 23}


"""@cart_router.get(
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
    response_model=PagedResponseSchema[CartOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_logged_user_carts(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[CartOutputSchema]:
    return get_all_user_carts(
        db, request_user.id, page_params, request.query_params.multi_items()
    )


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
"""