import pytest
from sqlalchemy.orm import Session

from src.apps.products.schemas import CategoryOutputSchema, ProductOutputSchema
from src.apps.products.services.product_services import (
    create_product,
    remove_single_product_from_store,
    get_all_products,
    get_single_product_or_inventory,
    update_single_product,
)
from src.apps.user.schemas import UserOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    QuantityLowerThanAmountOfProductItemsInCartsException,
    ProductAlreadyRemovedFromStore
)
from src.core.factories import (
    CartInputSchemaFactory,
    CartItemInputSchemaFactory,
    InventoryInputSchemaFactory,
    InventoryUpdateSchemaFactory,
    ProductInputSchemaFactory,
    ProductUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import DB_PRODUCT_SCHEMAS


def test_create_product_that_already_exists(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    with pytest.raises(AlreadyExists):
        create_product(sync_session, DB_PRODUCT_SCHEMAS[0])


def test_if_only_one_product_was_returned(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    product = get_single_product_or_inventory(sync_session, db_products[1].id)

    assert product.id == db_products[1].id


def test_raise_exception_while_getting_nonexistent_product(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_product_or_inventory(sync_session, generate_uuid())


def test_if_multiple_products_were_returned(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    products = get_all_products(sync_session, PageParams(page=1, size=5))
    assert products.total == len(db_products)


def test_raise_exception_while_updating_nonexistent_product(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    inventory_data = InventoryInputSchemaFactory().generate()
    update_data = ProductInputSchemaFactory().generate(inventory=inventory_data)
    with pytest.raises(DoesNotExist):
        update_single_product(sync_session, update_data, generate_uuid())


def test_product_quantity_cannot_be_lower_than_the_items_amount_in_the_carts(
    sync_session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
    db_categories: list[CategoryOutputSchema],
):
    from src.apps.orders.services.cart_items_services import create_cart_item
    from src.apps.orders.services.cart_services import create_cart

    product_quantity = 50
    inventory_data = InventoryInputSchemaFactory().generate(quantity=product_quantity)
    product_data = ProductInputSchemaFactory().generate(
        category_ids=[db_categories[0].id], inventory=inventory_data
    )

    product = create_product(sync_session, product_data)

    cart_1 = create_cart(sync_session, db_user.id)
    cart_item_product_quantity = 20
    cart_item_input_1 = CartItemInputSchemaFactory().generate(
        quantity=cart_item_product_quantity, product_id=product.id
    )
    cart_item_1 = create_cart_item(sync_session, cart_item_input_1, cart_1.id)

    product = get_single_product_or_inventory(sync_session, product_id=product.id)

    inventory_update_data = InventoryUpdateSchemaFactory().generate(quantity=10)
    update_data = ProductUpdateSchemaFactory().generate(inventory=inventory_update_data)

    with pytest.raises(QuantityLowerThanAmountOfProductItemsInCartsException):
        update_single_product(sync_session, update_data, product.id)


def test_cart_total_price_remains_correct_when_product_price_changes(
    sync_session,
    db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema
):
    from src.apps.orders.services.cart_items_services import create_cart_item, get_single_cart_item
    from src.apps.orders.services.cart_services import create_cart, get_single_cart
    
    cart_1 = create_cart(sync_session, db_user.id)
    quantity = 10
    cart_item_input_1 = CartItemInputSchemaFactory().generate(
        quantity=quantity, product_id=db_products[0].id
    )
    cart_item_1 = create_cart_item(sync_session, cart_item_input_1, cart_1.id)

    price = 5.3
    update_data = ProductUpdateSchemaFactory().generate(price=5.3)
    update_single_product(sync_session, update_data, db_products[0].id)
    
    cart_1 = get_single_cart(sync_session, cart_1.id)
    cart_item_1 = get_single_cart_item(sync_session, cart_item_1.id)
    
    assert cart_1.cart_total_price == price * quantity
    assert cart_item_1.cart_item_price == price * quantity
    

def test_if_product_can_have_occupied_name(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    inventory_data = InventoryInputSchemaFactory().generate()
    product_data = ProductInputSchemaFactory().generate(
        name=DB_PRODUCT_SCHEMAS[0].name, inventory=inventory_data
    )
    with pytest.raises(IsOccupied):
        update_single_product(sync_session, product_data, db_products[1].id)


def test_raise_exception_while_removing_nonexistent_product_from_store(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    with pytest.raises(DoesNotExist):
        remove_single_product_from_store(sync_session, generate_uuid())


def test_raise_exception_while_removing_product_from_store_that_is_already_removed(
    sync_session: Session, db_products: list[ProductOutputSchema]
):
    remove_single_product_from_store(sync_session, db_products[0].id)
    with pytest.raises(ProductAlreadyRemovedFromStore):
        remove_single_product_from_store(sync_session, db_products[0].id)
