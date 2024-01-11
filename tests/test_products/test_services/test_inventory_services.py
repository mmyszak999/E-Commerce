import pytest
from sqlalchemy.orm import Session

from src.apps.products.schemas import InventoryOutputSchema
from src.apps.products.schemas import ProductOutputSchema
from src.apps.products.services.inventory_services import (
    get_all_inventories,
    get_single_inventory,
    update_single_inventory,
)
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied
from src.core.factories import InventoryInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.utils.utils import generate_uuid
from tests.test_products.conftest import DB_INVENTORY_SCHEMAS


def test_if_only_one_inventory_was_returned(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema]
):
    inventory = get_single_inventory(sync_session, db_inventories.results[0].id)

    assert inventory.id == db_inventories.results[0].id


def test_raise_exception_while_getting_nonexistent_inventory(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema]
):
    with pytest.raises(DoesNotExist):
        get_single_inventory(sync_session, generate_uuid())


def test_if_multiple_inventories_were_returned(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema]
):
    inventories = get_all_inventories(sync_session, PageParams())
    assert inventories.total == len(DB_INVENTORY_SCHEMAS)


def test_raise_exception_while_updating_nonexistent_inventory(
    sync_session: Session,
    db_products: list[ProductOutputSchema],
    db_inventories: list[InventoryOutputSchema]
):
    update_data = InventoryInputSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        update_single_inventory(sync_session, update_data, generate_uuid())

