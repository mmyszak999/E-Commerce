from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.user.models import User
from src.apps.user.schemas import AddressOutputSchema, AddressUpdateSchema
from src.apps.user.services.address_services import (
    get_all_addresses,
    get_single_address,
    update_single_address,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

address_router = APIRouter(prefix="/addresses", tags=["address"])


@address_router.get(
    "/",
    response_model=PagedResponseSchema[AddressOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_addresses(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[AddressOutputSchema]:
    check_if_staff(request_user)
    return get_all_addresses(db, page_params, request.query_params.multi_items())


@address_router.get(
    "/{address_id}",
    response_model=AddressOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_address(
    address_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> AddressOutputSchema:
    check_if_staff(request_user)
    return get_single_address(db, address_id)


@address_router.patch(
    "/{address_id}",
    response_model=AddressOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_address(
    address_id: str,
    address: AddressUpdateSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> AddressOutputSchema:
    check_if_staff(request_user)
    return update_single_address(db, address, address_id)
