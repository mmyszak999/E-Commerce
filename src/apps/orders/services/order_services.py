import datetime
from typing import Union

from fastapi import BackgroundTasks
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session, selectinload

from src.apps.emails.services import (
    send_awaiting_for_payment_mail,
    send_payment_confirmaion_mail,
)
from src.apps.orders.models import Cart, Order
from src.apps.orders.schemas import (
    OrderItemOutputSchema,
    OrderOutputSchema,
    UserOrderOutputSchema,
)
from src.apps.orders.services.order_items_services import create_order_items
from src.apps.payments.models import Payment
from src.apps.payments.schemas import PaymentOutputSchema
from src.apps.products.models import Product
from src.apps.user.models import User
from src.core.exceptions import (
    DoesNotExist,
    EmptyCartException,
    OrderAlreadyCancelledException,
    PaymentAlreadyAccepted,
    OrderCancelledException
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists


def create_order(
    session: Session, user_id: str, cart_id: str, background_tasks: BackgroundTasks
) -> UserOrderOutputSchema:
    if not (user_object := if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)

    if not (cart_object := if_exists(Cart, "id", cart_id, session)):
        raise DoesNotExist(Cart.__name__, "id", cart_id)

    if not cart_object.cart_items:
        raise EmptyCartException

    new_order = Order(user_id=user_id)
    session.add(new_order)
    session.commit()

    create_order_items(
        session=session, order=new_order, cart_items=cart_object.cart_items
    )
    new_order.total_order_price = cart_object.cart_total_price
    session.add(new_order)
    session.commit()

    statement = delete(Cart).filter(Cart.id == cart_id)
    session.execute(statement)
    session.commit()
    
    send_awaiting_for_payment_mail(
        user_object.email, session, background_tasks, new_order.id 
    )
    return UserOrderOutputSchema.from_orm(new_order)


def get_single_order(
    session: Session, order_id: str, as_staff: bool = False
) -> Union[OrderOutputSchema, UserOrderOutputSchema]:
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, "id", order_id)

    if as_staff:
        return OrderOutputSchema.from_orm(order_object)
    return UserOrderOutputSchema.from_orm(order_object)


def get_all_orders(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
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
    session: Session,
    user_id: str,
    page_params: PageParams,
    query_params: list[tuple] = None,
) -> PagedResponseSchema[OrderOutputSchema]:
    query = (
        select(Order).filter(User.id == user_id).join(User, Order.user_id == User.id)
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


def cancel_orders_with_exceeded_payment_deadline(session: Session) -> None:
    invalid_orders = (
        session.scalars(
            select(Order).filter(
                Order.waiting_for_payment == True,
                Order.cancelled == False,
                Order.payment_deadline < datetime.datetime.now(),
            )
        )
        .unique()
        .all()
    )

    [cancel_single_order(session, order.id, True) for order in invalid_orders]


def cancel_single_order(
    session: Session, order_id: int, exceeded_payment_deadline: bool = False
):
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, "id", order_id)

    if order_object.cancelled:
        raise OrderAlreadyCancelledException

    for order_item in order_object.order_items:
        if not (
            product_object := if_exists(Product, "id", order_item.product_id, session)
        ):
            raise DoesNotExist(Product.__name__, "id", order_item.product_id)

        product_object.inventory.quantity_for_cart_items += order_item.quantity
        session.add(product_object)

    if exceeded_payment_deadline:
        order_object.waiting_for_payment = False
        session.add(order_object)

    order_object.cancelled = True
    session.add(order_object)
    session.commit()


def fulfill_order(
    session: Session,
    stripe_session, payment_intent,
    background_tasks: BackgroundTasks,
    order_id: str = None, amount: int = None,
    testing: bool = False
) -> None:
    if not order_id:
        order_id = stripe_session["metadata"]["order_id"]
    
    if not amount:
        amount = payment_intent["amount"] / 100
        
    stripe_charge_id = payment_intent["latest_charge"]
    
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, "id", order_id)
    
    if order_object.cancelled:
        raise OrderCancelledException
    
    if order_object.payment_accepted:
        raise PaymentAlreadyAccepted
    
    order_object.order_accepted = True
    order_object.payment_accepted = True
    order_object.waiting_for_payment = False
    session.add(order_object)
    
    new_payment = Payment(
        stripe_charge_id=stripe_charge_id,
        amount=amount,
        order_id=order_id,
        user_id=order_object.user_id
    )
    session.add(new_payment)
    
    for order_item in order_object.order_items:
        if not (
            product_object := if_exists(Product, "id", order_item.product_id, session)
        ):
            raise DoesNotExist(Product.__name__, "id", order_item.product_id)

        product_object.inventory.quantity -= order_item.quantity
        product_object.inventory.sold += order_item.quantity
        session.add(product_object)
        
    session.add(order_object)
    send_payment_confirmaion_mail(
        order_object.user.email, session, background_tasks, order_id
    )
    session.commit()
    if testing:
        return PaymentOutputSchema.from_orm(new_payment)
    return