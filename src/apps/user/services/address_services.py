from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.apps.user.models import UserAddress
from src.apps.user.schemas import AddressOutputSchema, AddressUpdateSchema

from src.core.exceptions import DoesNotExist
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists


def get_single_address(session: Session, address_id: int) -> AddressOutputSchema:
    if not (address_object := if_exists(UserAddress, "id", address_id, session)):
        raise DoesNotExist(UserAddress.__name__, "id", address_id)

    return AddressOutputSchema.from_orm(address_object)


def get_all_addresses(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[AddressOutputSchema]:
    query = select(UserAddress)

    if query_params:
        query = filter_and_sort_instances(query_params, query, UserAddress)

    return paginate(
        query=query,
        response_schema=AddressOutputSchema,
        table=UserAddress,
        page_params=page_params,
        session=session,
    )

def update_single_address(
    session: Session, address_input: AddressUpdateSchema, address_id: int
) -> AddressOutputSchema:
    if not if_exists(UserAddress, "id", address_id, session):
        raise DoesNotExist(UserAddress.__name__, "id", address_id)

    address_data = address_input.dict(exclude_unset=True)

    if address_data:
        statement = (
            update(UserAddress).filter(UserAddress.id == address_id).values(**address_data)
        )

        session.execute(statement)
        session.commit()

    return get_single_address(session, address_id=address_id)