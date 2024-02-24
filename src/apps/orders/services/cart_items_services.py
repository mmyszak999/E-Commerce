from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, selectinload, joinedload

from src.apps.orders.models import Cart, CartItem
from src.apps.orders.schemas import (CartItemInputSchema, CartItemOutputSchema, CartItemUpdateSchema)
from src.apps.products.models import Product
from src.apps.user.models import User
from src.core.exceptions import (DoesNotExist, ServiceException, ActiveCartException, ExceededItemQuantityException,
                                 NonPositiveCartItemQuantityException, EmptyCartException, NoSuchItemInCartException,
                                 CartItemWithZeroQuantityException)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists, calculate_item_price, validate_item_quantity


def create_cart_item(session: Session, cart_item: CartItemInputSchema, cart_id: str) -> CartItemOutputSchema:
    if not (cart_object := if_exists(Cart, "id", cart_id, session)):
        raise DoesNotExist(Cart.__name__, "id", cart_id)
    
    cart_item_data = cart_item.dict()
    product_id = cart_item_data.get("product_id")
    requested_quantity = cart_item_data.get("quantity")
    
    if not (product_object := if_exists(Product, "id", product_id, session)):
        raise DoesNotExist(Product.__name__, "id", product_id)
    
    item_in_cart_check = session.scalar(
        select(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id).limit(1)
    )
    
    available_quantity = product_object.inventory.quantity
    
    if not validate_item_quantity(available_quantity, requested_quantity):
        raise ExceededItemQuantityException(
            available_quantity, requested_quantity
        )
    
    if new_cart_item := item_in_cart_check:
        update_single_cart_item(
            session, new_cart_item, cart_object, product_object, requested_quantity
        )
        
    else:
        if requested_quantity == 0:
            raise NonPositiveCartItemQuantityException()
        
        cart_item_price = calculate_item_price(requested_quantity, product_object.price)
        cart_object.cart_total_price += cart_item_price
        session.add(cart_object)
        session.commit()
        
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
    print(cart_item_object.cart.user.username, "w0w")
    
    return CartItemOutputSchema.from_orm(cart_item_object)


def get_all_cart_items_for_single_cart(
    session: Session, cart_id: str, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema:
    query = select(CartItem).filter(CartItem.cart_id == cart_id)
    #.join(User, Cart.user_id == User.id)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Cart)

    return paginate(
        query=query,
        response_schema=CartItemOutputSchema,
        table=CartItem,
        page_params=page_params,
        session=session,
    )

def update_single_cart_item(
    session: Session, cart_item: CartItem, cart: Cart, product: Product, requested_quantity: int
) -> None:
    
    if requested_quantity == 0:
        statement = delete(CartItem).filter(CartItem.id == cart_item.id)
        session.execute(statement)
        session.commit()
                
        if not cart.cart_items:
            statement = delete(Cart).filter(Cart.id == cart.id)
            session.execute(statement)
            session.commit()
            raise EmptyCartException()
                
        raise CartItemWithZeroQuantityException()
                
    old_item_price = cart_item.cart_item_price
    new_item_price = calculate_item_price(requested_quantity, product.price)
            
    price_difference = old_item_price - new_item_price
    cart.cart_total_price -= price_difference
    session.add(cart)
    session.commit()
            
    cart_item.quantity = requested_quantity
    cart_item.cart_item_price = new_item_price
    session.add(cart_item)
    session.commit()
    
    
def update_cart_item(
    session: Session, cart_item_id: str, cart_item_input: CartItemUpdateSchema, cart_id: str
):
    if not (cart_item_object := if_exists(CartItem, "id", cart_item_id, session)):
        raise DoesNotExist(CartItem.__name__, "id", cart_item_id)
    
    if not (cart_object := if_exists(Cart, "id", cart_id, session)):
        raise DoesNotExist(Cart.__name__, "id", cart_id)
    
    cart_item_data = cart_item_input.dict()
    requested_quantity = cart_item_data.get("quantity")
    
    item_in_cart_check = cart_item_object.filter(CartItem.cart.id == cart_id).limit(1)
    
    if not (new_cart_item := item_in_cart_check):
        raise NoSuchItemInCartException
    
    if not (product_object := if_exists(Product, "id", new_cart_item.product.id, session)):
        raise DoesNotExist(Product.__name__, "id", new_cart_item.product.id)
    
    available_quantity = product_object.inventory.quantity
        
    if not validate_item_quantity(available_quantity, requested_quantity):
        raise ExceededItemQuantityException(
            available_quantity, requested_quantity
        )
            
    update_single_cart_item(
        session, cart_item_object, cart_object, product_object, requested_quantity)
    
    return get_single_cart_item(session, cart_item_id)


"""
def delete_single_cart(session: Session, cart_id: int):
    if not if_exists(Cart, "id", cart_id, session):
        raise DoesNotExist(Cart.__name__, "id", cart_id)

    statement = delete(Cart).filter(Cart.id == cart_id)
    result = session.execute(statement)
    session.commit()

    return result"""