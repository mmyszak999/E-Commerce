import pytest
from sqlalchemy.orm import Session

from src.apps.user.schemas import AddressOutputSchema, UserOutputSchema
from src.apps.user.services.address_services import (
    get_all_addresses,
    get_single_address,
    update_single_address,
)
from src.apps.user.services.user_services import get_all_users
from src.core.exceptions import DoesNotExist
from src.core.factories import AddressInputSchemaFactory
from src.core.pagination.models import PageParams
from src.core.utils.utils import generate_uuid
from tests.test_users.conftest import DB_ADDRESS_SCHEMAS, db_addresses, db_user


def test_if_only_one_address_was_returned(
    sync_session: Session,
    db_addresses: list[AddressOutputSchema],
):
    address = get_single_address(sync_session, db_addresses.results[0].id)

    assert address.id == db_addresses.results[0].id


def test_raise_exception_while_getting_nonexistent_address(
    sync_session: Session,
    db_addresses: list[AddressOutputSchema],
):
    with pytest.raises(DoesNotExist):
        get_single_address(sync_session, generate_uuid())


def test_if_multiple_addresses_were_returned(
    sync_session: Session,
    db_user: UserOutputSchema,
    db_staff_user: UserOutputSchema,
    db_addresses: list[AddressOutputSchema],
):
    addresses = get_all_addresses(sync_session, PageParams())

    assert addresses.total == get_all_users(sync_session, PageParams()).total


def test_raise_exception_while_updating_nonexistent_address(
    sync_session: Session,
    db_addresses: list[AddressOutputSchema],
):
    update_data = AddressInputSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        update_single_address(sync_session, update_data, generate_uuid())
