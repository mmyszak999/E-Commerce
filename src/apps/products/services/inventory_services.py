from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.apps.products.models import ProductInventory
from src.apps.products.schemas import InventoryInputSchema, InventoryOutputSchema

from src.core.exceptions import NegativeQuantityException, DoesNotExist
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists


def get_single_inventory(session: Session, inventory_id: int) -> InventoryOutputSchema:
    if not (inventory_object := if_exists(ProductInventory, "id", inventory_id, session)):
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
    if not if_exists(ProductInventory, "id", inventory_id, session):
        raise DoesNotExist(ProductInventory.__name__, "id", inventory_id)

    inventory_data = inventory_input.dict(exclude_unset=True)

    if inventory_data:
        if quantity := inventory_data.get("quantity") < 0:
            raise NegativeQuantityException(quantity)
    
        statement = (
            update(ProductInventory).filter(ProductInventory.id == inventory_id).values(**inventory_data)
        )

        session.execute(statement)
        session.commit()

    return get_single_inventory(session, inventory_id=inventory_id)
