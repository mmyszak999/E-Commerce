from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload

from src.apps.orders.models import Order
from src.apps.orders.schemas import OrderInputSchema, OrderOutputSchema
from src.apps.products.models import Product
from src.apps.user.models import User
from src.core.exceptions import DoesNotExist, ServiceException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists


def create_order(
    session: Session, order_input: OrderInputSchema, user_id: int
) -> OrderOutputSchema:
    pass
    """order_input_data = order_input.dict()

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

    return OrderOutputSchema.from_orm(new_order)"""


def get_single_order(
    session: Session, order_id: int, user_id: int
) -> OrderOutputSchema:
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, order_id)

    return OrderOutputSchema.from_orm(order_object)


def get_all_orders(
    session: Session, page_params: PageParams, query_params: list[tuple]
) -> PagedResponseSchema:
    query = select(Order).options(selectinload(Order.products))

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
    session: Session, user_id: int, page_params: PageParams, query_params: list[tuple]
) -> PagedResponseSchema[OrderOutputSchema]:
    query = (
        select(Order).filter(User.id == user_id).options(selectinload(Order.products))
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


