from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.apps.products.models import ProductInventory
from src.apps.products.schemas import InventoryInputSchema, InventoryOutputSchema
from src.core.exceptions import DoesNotExist, NegativeQuantityException
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists


def get_single_inventory(session: Session, inventory_id: int) -> InventoryOutputSchema:
    if not (
        inventory_object := if_exists(ProductInventory, "id", inventory_id, session)
    ):
        raise DoesNotExist(ProductInventory.__name__, "id", inventory_id)

    return InventoryOutputSchema.from_orm(inventory_object)


def get_all_inventories(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[InventoryOutputSchema]:
    query = select(ProductInventory)

    if query_params:
        query = filter_and_sort_instances(query_params, query, ProductInventory)

    return paginate(
        query=query,
        response_schema=InventoryOutputSchema,
        table=ProductInventory,
        page_params=page_params,
        session=session,
    )


def update_single_inventory(
    session: Session, inventory_input: InventoryInputSchema, inventory_id: int
) -> InventoryOutputSchema:
    if not (inventory_object := if_exists(ProductInventory, "id", inventory_id, session)):
        raise DoesNotExist(ProductInventory.__name__, "id", inventory_id)

    inventory_data = inventory_input.dict(exclude_unset=True)
    
    if inventory_object.quantity != inventory_data.get("quantity"): #50 != 70
        quantity_difference = inventory_object.quantity - inventory_data.get("quantity") #50 - 30 = 20
        inventory_data["quantity_for_cart_items"] = max(0, inventory_object.quantity_for_cart_items - quantity_difference)
        """quantity = 50, quantity_for_cart_items=30, in carts = 20
        new quantity = 10
        quantity = 10, quantity_for_cart_items=30-40=-10=>0, in_carts=20
        so we need to check if new quantity is bigger than product amount in carts
        because in the case like the previous one we should not be able to delete the items
        from the client's carts
        so new quantity cant be lower than the amount if product items in carts
        if new quantity is 40, and in cart are 20 items, so available ones drops from 30 to 20
        and in-cart amount stays the same, always stays the same btw
        if new quantity is 20, and in cart are 20 items, avaiable ones drops to 0 
        and we leave only the ones in the carts
        if new quantity is 10 and in cart are 20 items, we reject that update cuz new
        quantity cant be lower than in-cart item amount, we cant remove some of the items
        from the carts, to do tomorrow"""
        

    statement = (
        update(ProductInventory)
        .filter(ProductInventory.id == inventory_id)
        .values(**inventory_data)
    )

    session.execute(statement)
    session.commit()

    return get_single_inventory(session, inventory_id=inventory_id)
