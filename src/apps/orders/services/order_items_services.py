from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload

from src.apps.orders.models import Order, CartItem, OrderItem
from src.apps.products.models import Product
from src.core.exceptions import DoesNotExist, ServiceException, EmptyCartException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists, validate_item_quantity


def create_order_items(
    session: Session, order: Order, cart_items: list[CartItem]
):
    if not cart_items:
        raise EmptyCartException
    
    for cart_item in cart_items:
        if not (product_object := if_exists(Product, "id", cart_item.product_id, session)):
            raise DoesNotExist(Product.__name__, "id", cart_item.product_id)
        
        print(order.__dict__, "w", order.id)
        order_item_data = dict()
        
        order_item_data["product_id"] = cart_item.product_id
        order_item_data["quantity"] = cart_item.quantity
        order_item_data["order_id"] = order.id    
        order_item_data["order_item_price"] = cart_item.cart_item_price
        
        validate_item_quantity(product_object.inventory.quantity, cart_item.quantity)
        
        new_order_item = OrderItem(**order_item_data)
        print(new_order_item.__dict__, "nn")
        session.add(new_order_item)
    session.add(order)
    session.commit()
    return
        
        