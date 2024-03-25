from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, joinedload, selectinload

from src.apps.orders.models import Cart, CartItem
from src.apps.orders.schemas import (
    CartItemInputSchema,
    CartItemOutputSchema,
    CartItemUpdateSchema,
    CartOutputSchema,
)
from src.apps.orders.services.cart_items_services import delete_single_cart_item
from src.apps.products.models import Product
from src.apps.user.models import User
from src.core.exceptions import ActiveCartException, DoesNotExist, ServiceException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists


def create_cart(session: Session, user_id: str) -> CartOutputSchema:
    if not (user_object := if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)

    if user_object.carts:
        raise ActiveCartException()

    new_cart = Cart(user_id=user_id)
    session.add(new_cart)
    session.commit()

    return CartOutputSchema.from_orm(new_cart)


def get_single_cart(session: Session, cart_id: int) -> CartOutputSchema:
    if not (cart_object := if_exists(Cart, "id", cart_id, session)):
        raise DoesNotExist(Cart.__name__, "id", cart_id)

    if not (user_object := if_exists(User, "id", cart_object.user_id, session)):
        raise DoesNotExist(User.__name__, "user_id", cart_object.user_id)

    return CartOutputSchema.from_orm(cart_object)


def get_all_carts(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema:
    query = select(Cart).join(User, Cart.user_id == User.id)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Cart)

    return paginate(
        query=query,
        response_schema=CartOutputSchema,
        table=Cart,
        page_params=page_params,
        session=session,
    )


def get_all_user_carts(
    session: Session,
    user_id: int,
    page_params: PageParams,
    query_params: list[tuple] = None,
) -> PagedResponseSchema[CartOutputSchema]:
    query = select(Cart).join(User, Cart.user_id == User.id).filter(User.id == user_id)
    if query_params:
        query = filter_and_sort_instances(query_params, query, Cart)

    return paginate(
        query=query,
        response_schema=CartOutputSchema,
        table=Cart,
        page_params=page_params,
        session=session,
    )


def delete_single_cart(session: Session, cart_id: int):
    if not (cart_object := if_exists(Cart, "id", cart_id, session)):
        raise DoesNotExist(Cart.__name__, "id", cart_id)

    [
        delete_single_cart_item(
            session, cart_object.id, cart_item.id, cart_removing=True
        )
        for cart_item in cart_object.cart_items
    ]
    statement = delete(Cart).filter(Cart.id == cart_id)
    result = session.execute(statement)
    session.commit()

    return result
