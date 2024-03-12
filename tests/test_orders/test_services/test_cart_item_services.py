import pytest
from sqlalchemy.orm import Session
from copy import deepcopy

from src.apps.orders.schemas import CartOutputSchema, CartItemOutputSchema, CartItemInputSchema
from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.apps.orders.services.cart_services import get_single_cart, create_cart
from src.apps.orders.services.cart_items_services import (
    create_cart_item,
    get_single_cart_item,
    get_all_cart_items_for_single_cart,
    update_cart_item,
    delete_single_cart_item
)
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    AlreadyExists, DoesNotExist, IsOccupied, ExceededItemQuantityException,
    NonPositiveCartItemQuantityException, NoSuchItemInCartException,
    EmptyCartException, CartItemWithZeroQuantityException)

from src.core.factories import CartInputSchemaFactory, CartItemInputSchemaFactory, CartItemUpdateSchemaFactory
from src.core.pagination.models import PageParams
from src.core.utils.utils import generate_uuid
from tests.test_orders.conftest import db_carts
from tests.test_users.conftest import db_user


def test_raise_exception_when_cart_item_created_with_nonexistent_cart_id(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    cart_item_input = CartItemInputSchemaFactory().generate(product_id=db_products[1].id)
    with pytest.raises(DoesNotExist):
        create_cart_item(sync_session, cart_item_input, cart_id=generate_uuid())


def test_raise_exception_when_cart_item_created_with_nonexistent_product_id(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    cart_item_input = CartItemInputSchemaFactory().generate(product_id=generate_uuid())
    with pytest.raises(DoesNotExist):
        create_cart_item(sync_session, cart_item_input, cart_id=db_carts.results[0].id)

def test_raise_exception_when_cart_item_created_with_too_big_quantity(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    cart_item_input = CartItemInputSchemaFactory().generate(quantity=222222222222222222, product_id=db_products[1].id)
    with pytest.raises(ExceededItemQuantityException):
        create_cart_item(sync_session, cart_item_input, cart_id=db_carts.results[0].id)

def test_raise_exception_when_provided_no_quantity(
    sync_session: Session, db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(quantity=0, product_id=db_products[0].id)
    with pytest.raises(NonPositiveCartItemQuantityException):
        create_cart_item(sync_session, cart_item_input, cart_id=cart.id)

def test_cart_will_contain_correct_total_items_price_after_adding_cart_item(
    sync_session: Session, db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = create_cart(sync_session, db_user.id)
    item_quantity, product = 5, db_products[2]
    
    current_cart_item_price = cart.cart_total_price

    cart_item_input = CartItemInputSchemaFactory().generate(quantity=item_quantity, product_id=db_products[0].id)
    result = create_cart_item(sync_session, cart_item_input, cart_id=cart.id)
    cart = get_single_cart(sync_session, cart.id)
    
    assert cart.cart_total_price == float(current_cart_item_price) + result.cart_item_price

def test_if_only_one_cart_item_was_returned(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    cart_item = get_single_cart_item(sync_session, db_cart_items.results[0].id)
    assert cart_item.id == db_cart_items.results[0].id


def test_raise_exception_while_getting_nonexistent_cart_item(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_cart_item(sync_session, generate_uuid())


def test_if_multiple_cart_items_were_returned(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    cart = db_carts.results[0]
    cart_item_input = CartItemInputSchemaFactory().generate(quantity=5, product_id=db_products[2].id)
    create_cart_item(sync_session, cart_item_input, cart_id=cart.id)
    
    cart_items = get_all_cart_items_for_single_cart(sync_session, cart.id ,PageParams(page=1, size=25))
    cart = get_single_cart(sync_session, cart.id)
    assert cart_items.total == len(cart.cart_items)


def test_raise_exception_when_cart_item_updated_with_nonexistent_cart_item_id(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    cart_item_input = CartItemUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        update_cart_item(sync_session, cart_item_input, cart_item_id=generate_uuid(), cart_id=db_carts.results[0].id)

def test_raise_exception_when_cart_item_updated_with_nonexistent_cart_id(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    cart_item_input = CartItemUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        update_cart_item(sync_session, cart_item_input, cart_item_id=db_cart_items.results[0].id, cart_id=generate_uuid())

def test_raise_exception_when_there_is_no_cart_item_with_provided_id(
    sync_session: Session, db_products: list[ProductOutputSchema], db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema
):
    cart_1 = create_cart(sync_session, db_user.id)
    cart_item_input_1 = CartItemInputSchemaFactory().generate(product_id=db_products[0].id)
    cart_item_1 = create_cart_item(sync_session, cart_item_input_1, cart_1.id)
    
    cart_2 = create_cart(sync_session, db_staff_user.id)
    cart_item_input_2 = CartItemInputSchemaFactory().generate(product_id=db_products[1].id)
    cart_item_2 = create_cart_item(sync_session, cart_item_input_2, cart_2.id)
    
    with pytest.raises(NoSuchItemInCartException):
        cart_item_update_input = CartItemUpdateSchemaFactory().generate()
        update_cart_item(sync_session, cart_item_update_input, cart_item_id=cart_item_2.id, cart_id=cart_1.id)

def test_raise_exception_when_cart_item_updated_with_too_big_quantity(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    cart_item_input = CartItemInputSchemaFactory().generate(quantity=222222222222222222222, product_id=db_products[1].id)
    with pytest.raises(ExceededItemQuantityException):
        create_cart_item(sync_session, cart_item_input, cart_id=db_carts.results[0].id)

def test_cart_will_contain_correct_total_items_price_after_updating_cart_item(
    sync_session: Session, db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    item_quantity = 44
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(product_id=db_products[0].id)
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    cart_item_input = CartItemUpdateSchemaFactory().generate(quantity=item_quantity)
    result = update_cart_item(sync_session, cart_item_input, cart_item_id=cart_item.id, cart_id=cart.id)
    cart = get_single_cart(sync_session, cart.id)
    cart_item = get_single_cart_item(sync_session, cart_item.id)
    
    assert cart_item.cart_item_price == item_quantity * cart_item.product.price
    assert cart_item.cart_item_price == cart.cart_total_price 

def test_cart_will_be_deleted_when_there_are_no_cart_items_left_while_updating(
    sync_session: Session, db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(product_id=db_products[0].id)
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)
    
    with pytest.raises(EmptyCartException):
        cart_item_input = CartItemUpdateSchemaFactory().generate(quantity=0)
        update_cart_item(sync_session, cart_item_input, cart_item_id=cart_item.id, cart_id=cart.id)
    
    with pytest.raises(DoesNotExist):
        get_single_cart(sync_session, cart.id)

def test_updated_cart_item_will_be_deleted_when_quantity_equals_to_zero(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    with pytest.raises(CartItemWithZeroQuantityException):
        cart = db_carts.results[1]
        cart_item = db_cart_items.results[0]

        cart_item_input = CartItemUpdateSchemaFactory().generate(quantity=0)
        update_cart_item(sync_session, cart_item_input, cart_item_id=cart_item.id, cart_id=cart.id)
    
    with pytest.raises(DoesNotExist):
        get_single_cart_item(sync_session, cart_item.id)

def test_raise_exception_when_cart_item_deleted_with_nonexistent_cart_id(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        delete_single_cart_item(sync_session, cart_id=generate_uuid(), cart_item_id=db_cart_items.results[0].id)

def test_cart_will_be_deleted_when_there_are_no_cart_items_left_while_deleting(
    sync_session: Session, db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(product_id=db_products[0].id)
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)
    with pytest.raises(EmptyCartException):
        delete_single_cart_item(sync_session, cart_id=cart.id, cart_item_id=cart_item.id)
    
    with pytest.raises(DoesNotExist):
        get_single_cart(sync_session, cart.id)

def test_raise_exception_when_cart_item_deleted_with_nonexistent_cart_item_id(
    sync_session: Session, db_carts: list[CartOutputSchema],
    db_cart_items: list[CartItemOutputSchema], db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        delete_single_cart_item(sync_session, cart_id=db_carts.results[0].id, cart_item_id=generate_uuid())


