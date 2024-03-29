from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload

from src.apps.orders.models import Order, Cart
from src.apps.orders.schemas import OrderOutputSchema, OrderItemOutputSchema
from src.apps.orders.services.order_items_services import create_order_items
from src.apps.products.models import Product
from src.apps.user.models import User
from src.core.exceptions import DoesNotExist, ServiceException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists


def create_order(
    session: Session, user_id: str, cart_id: str
) -> OrderOutputSchema:
    if not (user_object := if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, user_id)

    if not (cart_object := if_exists(Cart, "id", cart_id, session)):
        raise DoesNotExist(Cart.__name__, cart_id)
    
    new_order = Order(user_id=user_id)
    session.add(new_order)
    session.commit()
    
    create_order_items(session=session, order=new_order, cart_items=cart_object.cart_items)
    new_order.total_order_price = cart_object.cart_total_price
    session.add(new_order)
    session.commit()
    
    statement = delete(Cart).filter(Cart.id==cart_id)
    session.execute(statement)
    session.commit()
    return OrderOutputSchema.from_orm(new_order)


def get_single_order(
    session: Session, order_id: str
) -> OrderOutputSchema:
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, order_id)

    return OrderOutputSchema.from_orm(order_object)


def get_all_orders(
    session: Session, page_params: PageParams, query_params: list[tuple]
) -> PagedResponseSchema:
    query = select(Order)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Order)

    return paginate(
        query=query,
        response_schema=OrderOutputSchema,
        table=Order,
        page_params=page_params,
        session=session,
    )


def get_all_user_orders(
    session: Session, user_id: str, page_params: PageParams, query_params: list[tuple]
) -> PagedResponseSchema[OrderOutputSchema]:
    query = (
        select(Order).filter(User.id == user_id).options(selectinload(Order.order_items))
    )
    if query_params:
        query = filter_and_sort_instances(query_params, query, Order)

    return paginate(
        query=query,
        response_schema=OrderOutputSchema,
        table=Order,
        page_params=page_params,
        session=session,
    )


