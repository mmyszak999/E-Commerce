from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from sqlalchemy.orm import Session

from src.apps.orders.schemas import (
    CartItemInputSchema,
    CartItemOutputSchema,
    CartOutputSchema,
)
from src.apps.orders.services.cart_items_services import (
    create_cart_item,
    delete_invalid_cart_items,
    delete_single_cart_item,
    get_all_cart_items,
    get_all_cart_items_for_single_cart,
    get_single_cart_item,
    update_cart_item,
)
from src.apps.orders.services.cart_services import create_cart, get_single_cart
from src.apps.products.schemas import CategoryOutputSchema, ProductOutputSchema
from src.apps.products.services.product_services import (
    create_product,
    get_single_product_or_inventory,
    remove_single_product_from_store,
    update_single_product,
)
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    ActiveCartException,
    AlreadyExists,
    CartItemWithZeroQuantityException,
    DoesNotExist,
    EmptyCartException,
    ExceededItemQuantityException,
    IsOccupied,
    NonPositiveCartItemQuantityException,
    NoSuchItemInCartException,
    ProductRemovedFromStoreException,
)
from src.core.factories import (
    CartInputSchemaFactory,
    CartItemInputSchemaFactory,
    CartItemUpdateSchemaFactory,
    InventoryInputSchemaFactory,
    ProductInputSchemaFactory,
    ProductUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_orders.conftest import db_carts
from tests.test_users.conftest import db_user


def test_raise_exception_when_cart_item_created_with_nonexistent_cart_id(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    cart_item_input = CartItemInputSchemaFactory().generate(
        product_id=db_products[1].id
    )
    with pytest.raises(DoesNotExist):
        create_cart_item(sync_session, cart_item_input, cart_id=generate_uuid())


def test_raise_exception_when_cart_item_created_with_nonexistent_product_id(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    cart_item_input = CartItemInputSchemaFactory().generate(product_id=generate_uuid())
    with pytest.raises(DoesNotExist):
        create_cart_item(sync_session, cart_item_input, cart_id=db_carts.results[0].id)


def test_raise_exception_when_cart_item_created_with_too_big_quantity(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=222222222222222222, product_id=db_products[1].id
    )
    with pytest.raises(ExceededItemQuantityException):
        create_cart_item(sync_session, cart_item_input, cart_id=db_carts.results[0].id)


def test_raise_exception_when_provided_no_quantity(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=0, product_id=db_products[0].id
    )
    with pytest.raises(NonPositiveCartItemQuantityException):
        create_cart_item(sync_session, cart_item_input, cart_id=cart.id)


def test_cart_will_contain_correct_total_items_price_after_adding_cart_item(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    cart = create_cart(sync_session, db_user.id)
    item_quantity, product = 1, db_products[2]

    current_cart_item_price = cart.cart_total_price

    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=item_quantity, product_id=db_products[0].id
    )
    result = create_cart_item(sync_session, cart_item_input, cart_id=cart.id)
    cart = get_single_cart(sync_session, cart.id)

    assert cart.cart_total_price == current_cart_item_price + result.cart_item_price


def test_quantity_cart_item_will_be_managed_correctly_when_re_adding_the_product_to_the_cart(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    product = db_products[0]
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=10, product_id=product.id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    product = get_single_product_or_inventory(sync_session, product.id)
    assert (
        product.inventory.quantity_for_cart_items
        == product.inventory.quantity - cart_item.quantity
    )

    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=20, product_id=product.id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    product = get_single_product_or_inventory(sync_session, product.id)
    assert (
        product.inventory.quantity_for_cart_items
        == product.inventory.quantity - cart_item.quantity
    )

    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=5, product_id=product.id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    product = get_single_product_or_inventory(sync_session, product.id)
    assert (
        product.inventory.quantity_for_cart_items
        == product.inventory.quantity - cart_item.quantity
    )


def test_if_only_one_cart_item_was_returned(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    cart_item = get_single_cart_item(sync_session, db_cart_items.results[0].id)
    assert cart_item.id == db_cart_items.results[0].id


def test_raise_exception_while_getting_nonexistent_cart_item(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    with pytest.raises(DoesNotExist):
        get_single_cart_item(sync_session, generate_uuid())


def test_if_multiple_cart_items_were_returned(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    cart = db_carts.results[0]
    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=5, product_id=db_products[2].id
    )
    create_cart_item(sync_session, cart_item_input, cart_id=cart.id)

    cart_items = get_all_cart_items_for_single_cart(
        sync_session, cart.id, PageParams(page=1, size=25)
    )
    cart = get_single_cart(sync_session, cart.id)
    assert cart_items.total == len(cart.cart_items)


def test_raise_exception_when_cart_item_updated_with_nonexistent_cart_item_id(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    cart_item_input = CartItemUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        update_cart_item(
            sync_session,
            cart_item_input,
            cart_item_id=generate_uuid(),
            cart_id=db_carts.results[0].id,
        )


def test_raise_exception_when_cart_item_updated_with_nonexistent_cart_id(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    cart_item_input = CartItemUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        update_cart_item(
            sync_session,
            cart_item_input,
            cart_item_id=db_cart_items.results[0].id,
            cart_id=generate_uuid(),
        )


def test_raise_exception_when_there_is_no_cart_item_with_provided_id(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
):
    cart_1 = create_cart(sync_session, db_user.id)
    cart_item_input_1 = CartItemInputSchemaFactory().generate(
        product_id=db_products[0].id
    )
    cart_item_1 = create_cart_item(sync_session, cart_item_input_1, cart_1.id)

    cart_2 = create_cart(sync_session, db_staff_user.id)
    cart_item_input_2 = CartItemInputSchemaFactory().generate(
        product_id=db_products[1].id
    )
    cart_item_2 = create_cart_item(sync_session, cart_item_input_2, cart_2.id)

    with pytest.raises(NoSuchItemInCartException):
        cart_item_update_input = CartItemUpdateSchemaFactory().generate()
        update_cart_item(
            sync_session,
            cart_item_update_input,
            cart_item_id=cart_item_2.id,
            cart_id=cart_1.id,
        )


def test_raise_exception_when_cart_item_updated_with_too_big_quantity(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=222222222222222222222, product_id=db_products[1].id
    )
    with pytest.raises(ExceededItemQuantityException):
        create_cart_item(sync_session, cart_item_input, cart_id=db_carts.results[0].id)


def test_cart_will_contain_correct_total_items_price_after_updating_cart_item(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    item_quantity = 44
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(
        product_id=db_products[0].id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    cart_item_input = CartItemUpdateSchemaFactory().generate(quantity=item_quantity)
    result = update_cart_item(
        sync_session, cart_item_input, cart_item_id=cart_item.id, cart_id=cart.id
    )
    cart = get_single_cart(sync_session, cart.id)
    cart_item = get_single_cart_item(sync_session, cart_item.id)

    assert cart_item.cart_item_price == item_quantity * cart_item.product.price
    assert cart_item.cart_item_price == cart.cart_total_price


def test_cart_item_price_will_be_updated_when_product_price_changed(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(
        product_id=db_products[0].id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    product_input = ProductUpdateSchemaFactory().generate(price=5.00)
    update_single_product(sync_session, product_input, db_products[0].id)

    current_cart_item_price = cart_item.quantity * cart_item.product.price

    assert cart_item.cart_item_price == current_cart_item_price


def test_quantity_for_cart_items_will_change_when_cart_item_quantity_being_updated(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    product, quantity = db_products[0], 10
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=quantity, product_id=product.id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    product = get_single_product_or_inventory(sync_session, product.id)
    product_quantity_for_cart_items = product.inventory.quantity_for_cart_items

    quantity = 5
    cart_item_input = CartItemInputSchemaFactory().generate(
        quantity=quantity, product_id=product.id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    product = get_single_product_or_inventory(sync_session, product.id)

    assert (
        product.inventory.quantity_for_cart_items
        == product_quantity_for_cart_items + quantity
    )


def test_cart_will_be_deleted_when_there_are_no_cart_items_left_while_updating(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(
        product_id=db_products[0].id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    with pytest.raises(EmptyCartException):
        cart_item_input = CartItemUpdateSchemaFactory().generate(quantity=0)
        update_cart_item(
            sync_session, cart_item_input, cart_item_id=cart_item.id, cart_id=cart.id
        )

    with pytest.raises(DoesNotExist):
        get_single_cart(sync_session, cart.id)


def test_updated_cart_item_will_be_deleted_when_quantity_equals_to_zero(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input_1 = CartItemInputSchemaFactory().generate(
        product_id=db_products[0].id
    )
    cart_item_input_2 = CartItemInputSchemaFactory().generate(
        product_id=db_products[1].id
    )
    cart_item_1 = create_cart_item(sync_session, cart_item_input_1, cart.id)
    cart_item_2 = create_cart_item(sync_session, cart_item_input_2, cart.id)

    with pytest.raises(CartItemWithZeroQuantityException):
        cart_item_input = CartItemUpdateSchemaFactory().generate(quantity=0)
        update_cart_item(
            sync_session, cart_item_input, cart_item_id=cart_item_1.id, cart_id=cart.id
        )

    with pytest.raises(DoesNotExist):
        get_single_cart_item(sync_session, cart_item_1.id)


def test_raise_exception_when_cart_item_deleted_with_nonexistent_cart_id(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    with pytest.raises(DoesNotExist):
        delete_single_cart_item(
            sync_session,
            cart_id=generate_uuid(),
            cart_item_id=db_cart_items.results[0].id,
        )


def test_cart_will_be_deleted_when_there_are_no_cart_items_left_while_deleting(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(
        product_id=db_products[0].id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)
    with pytest.raises(EmptyCartException):
        delete_single_cart_item(
            sync_session, cart_id=cart.id, cart_item_id=cart_item.id
        )

    with pytest.raises(DoesNotExist):
        get_single_cart(sync_session, cart.id)


def test_raise_exception_when_cart_item_deleted_with_nonexistent_cart_item_id(
    sync_session: Session,
    db_carts: PagedResponseSchema[CartOutputSchema],
    db_cart_items: PagedResponseSchema[CartItemOutputSchema],
    db_products: list[ProductOutputSchema],
):
    with pytest.raises(DoesNotExist):
        delete_single_cart_item(
            sync_session, cart_id=db_carts.results[0].id, cart_item_id=generate_uuid()
        )


def test_if_cart_price_and_quantity_are_managed_correctly_when_cart_item_was_deleted(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    product_1, product_2 = db_products[0], db_products[1]
    quantity_1, quantity_2 = 10, 20

    cart_1 = create_cart(sync_session, db_user.id)
    cart_item_input_1 = CartItemInputSchemaFactory().generate(
        quantity=quantity_1, product_id=db_products[0].id
    )
    cart_item_1 = create_cart_item(sync_session, cart_item_input_1, cart_1.id)

    cart_item_input_2 = CartItemInputSchemaFactory().generate(
        quantity=quantity_2, product_id=db_products[1].id
    )
    cart_item_2 = create_cart_item(sync_session, cart_item_input_2, cart_1.id)

    cart_1 = get_single_cart(sync_session, cart_1.id)
    cart_1_price = cart_1.cart_total_price
    product_1 = get_single_product_or_inventory(sync_session, product_1.id)
    product_1_quantity_for_cart_items = product_1.inventory.quantity_for_cart_items

    delete_single_cart_item(
        sync_session, cart_id=cart_1.id, cart_item_id=cart_item_1.id
    )

    product_1 = get_single_product_or_inventory(sync_session, product_1.id)
    cart_1 = get_single_cart(sync_session, cart_1.id)

    assert (
        product_1.inventory.quantity_for_cart_items
        == product_1_quantity_for_cart_items + quantity_1
    )
    assert cart_1.cart_total_price == cart_1_price - (quantity_1 * product_1.price)


def test_invalid_cart_items_are_deleted_after_30_minutes_in_the_cart(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_input = CartItemInputSchemaFactory().generate(
        product_id=db_products[0].id
    )
    cart_item = create_cart_item(sync_session, cart_item_input, cart.id)

    delete_invalid_cart_items(sync_session)

    cart_items = get_all_cart_items(sync_session, PageParams(page=1, size=25))
    assert cart_items.total == 1

    with freeze_time(str(datetime.now() + timedelta(minutes=15))):
        cart_item_input_2 = CartItemInputSchemaFactory().generate(
            product_id=db_products[1].id
        )
        cart_item_2 = create_cart_item(sync_session, cart_item_input_2, cart.id)

        cart_items = get_all_cart_items(sync_session, PageParams(page=1, size=25))
        assert cart_items.total == 2

    with freeze_time(str(datetime.now() + timedelta(minutes=30))):
        delete_invalid_cart_items(sync_session)
        cart_items = get_all_cart_items(sync_session, PageParams(page=1, size=25))
        assert cart_items.total == 1

        with pytest.raises(DoesNotExist):
            get_single_cart_item(sync_session, cart_item.id)

    with freeze_time(str(datetime.now() + timedelta(minutes=45))):
        with pytest.raises(EmptyCartException):
            delete_invalid_cart_items(sync_session)

        cart_items = get_all_cart_items(sync_session, PageParams(page=1, size=25))
        assert cart_items.total == 0

        with pytest.raises(DoesNotExist):
            get_single_cart_item(sync_session, cart_item.id)

        with pytest.raises(DoesNotExist):
            get_single_cart(sync_session, cart.id)


def test_cart_item_will_be_deleted_when_related_product_is_removed_from_store(
    sync_session: Session,
    db_user: UserOutputSchema,
    db_products: list[ProductOutputSchema],
):
    cart = create_cart(sync_session, db_user.id)
    cart_item_data = CartItemInputSchemaFactory().generate(product_id=db_products[0].id)
    cart_item = create_cart_item(sync_session, cart_item_data, cart.id)

    product_id = cart_item.product.id

    cart = get_single_cart(sync_session, cart.id)
    assert len(cart.cart_items) == 1

    result = remove_single_product_from_store(sync_session, product_id)
    product = get_single_product_or_inventory(sync_session, product_id)

    assert product.removed_from_store == True

    with pytest.raises(DoesNotExist):
        get_single_cart_item(sync_session, cart_item.id)


def test_raise_exception_when_creating_cart_item_with_product_removed_from_store(
    sync_session: Session,
    db_user: UserOutputSchema,
    db_products: list[ProductOutputSchema],
):
    cart = create_cart(sync_session, db_user.id)

    remove_single_product_from_store(sync_session, db_products[1].id)
    product = get_single_product_or_inventory(sync_session, db_products[1].id)
    assert product.removed_from_store == True

    cart_item_data = CartItemInputSchemaFactory().generate(product_id=product.id)
    with pytest.raises(ProductRemovedFromStoreException):
        create_cart_item(sync_session, cart_item_data, cart.id)
