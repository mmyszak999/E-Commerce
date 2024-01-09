from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    InventoryInputSchema,
    InventoryOutputSchema
)
from src.apps.products.services.inventory_services import (
    get_all_inventories,
    get_single_inventory,
    update_single_inventory
)
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

inventory_router = APIRouter(prefix="/inventory", tags=["inventory"])


@inventory_router.get(
    "/",
    response_model=PagedResponseSchema[InventoryOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_inventories(
    request: Request,
    db: Session = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[InventoryOutputSchema]:
    return get_all_inventories(db, page_params, request.query_params.multi_items())


@inventory_router.get(
    "/{inventory_id}",
    response_model=InventoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_inventory(
    inventory_id: str,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> InventoryOutputSchema:
    check_if_staff(request_user)
    return get_single_inventory(db, inventory_id)


@inventory_router.patch(
    "/{inventory_id}",
    response_model=InventoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
def update_inventory(
    inventory_id: str,
    inventory: InventoryInputSchema,
    db: Session = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> InventoryOutputSchema:
    check_if_staff(request_user)
    return update_single_inventory(db, inventory, inventory_id)