from sqlalchemy import delete, select, update, insert
from sqlalchemy.orm import Session

from src.apps.user.models import User
from src.apps.products.models import Product
from src.apps.orders.schemas import (
    OrderInputSchema,
    OrderOutputSchema
)
from src.apps.orders.models import Order, order_product_association_table
from src.core.exceptions import (
    DoesNotExist,
    AlreadyExists,
    IsOccupied,
    ServiceException
)
from src.core.utils import if_exists
from src.core.pagination.services import paginate
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.models import PageParams


def create_order(session: Session, order: OrderInputSchema) -> OrderOutputSchema:
    order_data = order.dict()
    
    user_id = order_data.pop('user_id')
    user = session.scalar(select(User).filter(User.id==user_id).limit(1))
    product_ids = order_data.pop('product_ids')
    products = session.scalars(select(Product).where(Product.id.in_(categories_ids))).all()

    order_data['user'], order_data['products'] = user, products
    new_order = Order(**orderdata)
    session.add(new_order)
    session.commit()

    return OrderOutputSchema.from_orm(new_product)

def get_single_order(session: Session, order_id: int) -> OrderOutputSchema:
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, order_id)

    return OrderOutputSchema.from_orm(order_object)

def get_all_orders(session: Session, page_params: PageParams) -> PagedResponseSchema[OrderOutputSchema]:
    query = select(Order)

    return paginate(query=query, response_schema=OrderOutputSchema, table=Order, page_params=page_params, session=session)

def update_single_order(session: Session, order_input: OrderInputSchema, order_id: int) -> OrderOutputSchema:
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, order_id)
    
    order_data = order_input.dict()
    incoming_products = set(order_data['products_ids'])
    current_products = set(product.id for product in order_object.products)
    
    if to_delete := current_products - incoming_products:
        session.execute(delete(order_product_association_table).where(Product.id.in_(to_delete)))
    
    if to_insert := incoming_products - current_products:
        rows = [{"order_id": order_id, "product_id": product_id} for product_id in to_insert]
        session.execute(insert(order_product_association_table).values(rows))

    order_data.pop('products_ids')
    statement = update(Order).filter(Order.id==order_id).values(**order_data(exclude_unset=True))
    
    session.execute(statement)
    session.commit()
    session.refresh(order_object)
    
    return get_single_order(session, order_id=order_id)

def delete_all_orders(session: Session):
    statement = delete(Order)
    result = session.execute(statement)
    session.commit()

    return result    

def delete_single_order(session: Session, order_id: int):
    if not (order_object := if_exists(Order, "id", order_id, session)):
        raise DoesNotExist(Order.__name__, order_id)

    statement = delete(Order).filter(Order.id == order_id)
    result = session.execute(statement)
    session.commit()

    return result
