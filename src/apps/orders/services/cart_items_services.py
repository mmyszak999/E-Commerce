from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload, joinedload

from src.apps.orders.models import Cart, CartItem
from src.apps.orders.schemas import (CartItemInputSchema, CartItemOutputSchema, CartItemUpdateSchema)
from src.apps.products.models import Product
from src.apps.user.models import User
from src.core.exceptions import DoesNotExist, ServiceException, ActiveCartException, ExceededItemQuantityException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists, calculate_item_price, validate_item_quantity


def create_cart_item(session: Session, cart_item: CartItemInputSchema, cart_id: str) -> CartItemOutputSchema:
    """if not (user_object := if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)"""
    cart_item_data = cart_item.dict()
    product_id = cart_item_data.get("product_id")
    quantity = cart_item_data.get("quantity")
    
    if not (product_object := if_exists(Product, "id", product_id, session)):
        raise DoesNotExist(Product.__name__, "id", product_id)
    
    item_in_cart_check = session.scalar(
        select(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id).limit(1)
    )
    
    current_quantity = item_in_cart_check.quantity or 0
    available_quantity = product_object.inventory.quantity - current_quantity
    
    if not validate_item_quantity(available_quantity, quantity):
        raise ExceededItemQuantityException(
            available_quantity, quantity
        )
    
    if new_cart_item := item_in_cart_check:
        new_cart_item.quantity += quantity
        session.add(new_cart_item)
        session.commit()
    else: 
        cart_item_price = product_object.price * cart_item_data.get("quantity")
        cart_item_data['cart_item_price'] = cart_item_price
        cart_item_data["cart_id"] = cart_id
        new_cart_item = CartItem(**cart_item_data)
        session.add(new_cart_item)
        session.commit()
    
    return CartItemOutputSchema.from_orm(new_cart_item)

def get_single_cart_item(
    session: Session, cart_item_id: int
) -> CartItemOutputSchema:
    if not (cart_item_object := if_exists(CartItem, "id", cart_item_id, session)):
        raise DoesNotExist(CartItem.__name__, "id", cart_item_id)
    
    return CartItemOutputSchema.from_orm(cart_item_object)


"""def get_all_carts(
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
    session: Session, user_id: int, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[CartOutputSchema]:
    query = (
        select(Cart).join(User, Cart.user_id == User.id).filter(User.id == user_id)
    )
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
    if not if_exists(Cart, "id", cart_id, session):
        raise DoesNotExist(Cart.__name__, "id", cart_id)

    statement = delete(Cart).filter(Cart.id == cart_id)
    result = session.execute(statement)
    session.commit()

    return result"""