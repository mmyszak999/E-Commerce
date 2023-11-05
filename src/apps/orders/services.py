from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload

from src.apps.orders.models import Order, order_product_association_table
from src.apps.orders.schemas import OrderInputSchema, OrderOutputSchema
from src.apps.products.models import Product
from src.apps.user.models import User
from src.core.exceptions import DoesNotExist, ServiceException
from src.core.filters import Lookup
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.sort import Sort
from src.core.utils import (
    check_if_request_user,
    filter_query_param_values_extractor,
    if_exists,
)


def create_order(
    session: Session, order_input: OrderInputSchema, user_id: int
) -> OrderOutputSchema:
    order_input_data = order_input.dict()

    product_ids = order_input_data.pop("product_ids")
    products = session.scalars(select(Product).where(Product.id.in_(product_ids))).all()

    if not len(set(product_ids)) == len(products):
        raise ServiceException(
            "Amount of products in the order is not consistent. "
            "Check if all products exist!"
        )

    order_create_data = dict()
    order_create_data["user_id"], order_create_data["products"] = user_id, products
    new_order = Order(user_id=user_id, products=products)
    session.add(new_order)
    session.commit()

    return OrderOutputSchema.from_orm(new_order)


def get_single_order(
    session: Session, order_id: int, user_id: int
) -> OrderOutputSchema:
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, order_id)

    check_if_request_user(
        user_id, order_object.user_id, "You are not the owner of the order!"
    )

    return OrderOutputSchema.from_orm(order_object)


def get_all_orders(
    session: Session, page_params: PageParams, query_params: list[tuple]
) -> PagedResponseSchema:
    query = select(Order).options(selectinload(Order.products))

    orders = Lookup(Order, query)
    filter_params = filter_query_param_values_extractor(query_params)
    if filter_params:
        for param in filter_params:
            orders = orders.perform_lookup(*param)

    orders = Sort(Order, orders.inst)
    orders.set_sort_params(query_params)
    orders.get_sorted_instances()

    return paginate(
        query=orders.inst,
        response_schema=OrderOutputSchema,
        table=Order,
        page_params=page_params,
        session=session,
    )


def get_all_user_orders(
    session: Session, user_id: int, page_params: PageParams, query_params: list[tuple]
) -> PagedResponseSchema[OrderOutputSchema]:
    query = (
        select(Order).filter(User.id == user_id).options(selectinload(Order.products))
    )

    orders = Lookup(Order, query)
    filter_params = filter_query_param_values_extractor(query_params)
    if filter_params:
        for param in filter_params:
            orders = orders.perform_lookup(*param)

    orders = Sort(Order, orders.inst)
    orders.set_sort_params(query_params)
    orders.get_sorted_instances()

    return paginate(
        query=orders.inst,
        response_schema=OrderOutputSchema,
        table=Order,
        page_params=page_params,
        session=session,
    )


def update_single_order(
    session: Session, order_input: OrderInputSchema, order_id: int, user_id: int
) -> OrderOutputSchema:
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, order_id)

    check_if_request_user(
        user_id,
        order_object.user_id,
        "You can't update the order. You are not the owner of the order!",
    )

    order_data = order_input.dict(exclude_none=True, exclude_unset=True)

    if order_data.get("product_ids"):
        incoming_products = set(order_data["product_ids"])
        current_products = set(product.id for product in order_object.products)

        if to_delete := current_products - incoming_products:
            session.execute(
                delete(order_product_association_table)
                .where(Product.id.in_(to_delete))
                .options(selectinload(Order.products))
            )

        if to_insert := incoming_products - current_products:
            rows = [
                {"order_id": order_id, "product_id": product_id}
                for product_id in to_insert
            ]
            session.execute(
                insert(order_product_association_table)
                .values(rows)
                .options(selectinload(Order.products))
            )

        order_data.pop("product_ids")

        statement = update(Order).filter(Order.id == order_id).values(**order_data)

        session.execute(statement)
        session.commit()

    return get_single_order(session, order_id=order_id, user_id=user_id)


def delete_single_order(session: Session, order_id: int):
    if not if_exists(Order, "id", order_id, session):
        raise DoesNotExist(Order.__name__, order_id)

    statement = delete(Order).filter(Order.id == order_id)
    result = session.execute(statement)
    session.commit()

    return result
