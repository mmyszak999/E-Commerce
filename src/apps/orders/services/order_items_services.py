from typing import Union

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload

from src.apps.orders.models import Order, OrderItem
from src.apps.orders.schemas import OrderItemOutputSchema, UserOrderItemOutputSchema
from src.apps.products.models import Product
from src.core.exceptions import DoesNotExist, EmptyCartException, ServiceException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import (
    filter_and_sort_instances,
    if_exists,
    validate_item_quantity,
)


def create_order_items(session: Session, order: Order, cart_items: list[OrderItem]):
    if not cart_items:
        raise EmptyCartException

    for cart_item in cart_items:
        if not (
            product_object := if_exists(Product, "id", cart_item.product_id, session)
        ):
            raise DoesNotExist(Product.__name__, "id", cart_item.product_id)

        order_item_data = dict()

        order_item_data["product_id"] = cart_item.product_id
        order_item_data["quantity"] = cart_item.quantity
        order_item_data["order_id"] = order.id
        order_item_data["order_item_price"] = cart_item.cart_item_price

        validate_item_quantity(product_object.inventory.quantity, cart_item.quantity)

        new_order_item = OrderItem(**order_item_data)
        session.add(new_order_item)

    session.add(order)
    session.commit()
    return


def get_single_order_item(
    session: Session, order_item_id: str, as_staff: bool=False
) -> Union[UserOrderItemOutputSchema, OrderItemOutputSchema]:
    if not (order_item_object := if_exists(OrderItem, "id", order_item_id, session)):
        raise DoesNotExist(OrderItem.__name__, "id", order_item_id)

    if as_staff:
        return OrderItemOutputSchema.from_orm(order_item_object)
    return UserOrderItemOutputSchema.from_orm(order_item_object)


def get_all_order_items(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[OrderItemOutputSchema]:
    query = select(OrderItem).join(Product, OrderItem.product_id == Product.id)

    if query_params:
        query = filter_and_sort_instances(query_params, query, OrderItem)

    return paginate(
        query=query,
        response_schema=OrderItemOutputSchema,
        table=OrderItem,
        page_params=page_params,
        session=session,
    )


def get_all_order_items_for_single_order(
    session: Session,
    order_id: str,
    page_params: PageParams,
    query_params: list[tuple] = None,
) -> PagedResponseSchema[UserOrderItemOutputSchema]:
    query = (
        select(OrderItem)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(OrderItem.order_id == order_id)
    )

    if query_params:
        query = filter_and_sort_instances(query_params, query, OrderItem)

    return paginate(
        query=query,
        response_schema=UserOrderItemOutputSchema,
        table=OrderItem,
        page_params=page_params,
        session=session,
    )
