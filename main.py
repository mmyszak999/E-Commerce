from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from src.apps.admin.routers import admin_router
from src.apps.emails.routers import email_router
from src.apps.jwt.routers import jwt_router
from src.apps.orders.routers.order_routers import order_router
from src.apps.products.routers.category_routers import category_router
from src.apps.products.routers.product_routers import product_router
from src.apps.products.routers.inventory_routers import inventory_router
from src.apps.user.routers.user_routers import user_router
from src.apps.user.routers.address_routers import address_router
from src.apps.orders.routers.cart_routers import cart_router
from src.apps.orders.routers.cart_items_routers import cart_items_router

from src.core.exceptions import (
    AccountNotActivatedException,
    ActiveCartException,
    AlreadyExists,
    AuthenticationException,
    AuthorizationException,
    DoesNotExist,
    IsOccupied,
    ServiceException,
    NegativeQuantityException,
    ExceededItemQuantityException,
    NonPositiveCartItemQuantityException,
    EmptyCartException,
    NoSuchItemInCartException,
    QuantityLowerThanAmountOfProductItemsInCartsException
)

app = FastAPI()

root_router = APIRouter(prefix="/api")

root_router.include_router(user_router)
root_router.include_router(address_router)
root_router.include_router(jwt_router)
root_router.include_router(category_router)
root_router.include_router(product_router)
root_router.include_router(inventory_router)
root_router.include_router(order_router)
root_router.include_router(email_router)
root_router.include_router(admin_router)
root_router.include_router(cart_router)
root_router.include_router(cart_items_router)

app.include_router(root_router)


@app.exception_handler(AuthJWTException)
def handle_auth_jwt_exception(
    request: Request, exception: AuthJWTException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exception.message}
    )


@app.exception_handler(DoesNotExist)
def handle_does_not_exist(request: Request, exception: DoesNotExist) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exception)}
    )


@app.exception_handler(AlreadyExists)
def handle_already_exists(request: Request, exception: AlreadyExists) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(IsOccupied)
def handle_is_occupied(request: Request, exception: IsOccupied) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(ServiceException)
def handle_service_exception(
    request: Request, exception: ServiceException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(AuthenticationException)
def handle_authentication_exception(
    request: Request, exception: AuthenticationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(AuthorizationException)
def handle_authorization_exception(
    request: Request, exception: AuthorizationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exception)}
    )


@app.exception_handler(AccountNotActivatedException)
def handle_account_not_activated_exception(
    request: Request, exception: AccountNotActivatedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(NegativeQuantityException)
def handle_negative_quantity_exception(
    request: Request, exception: NegativeQuantityException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(ActiveCartException)
def handle_active_cart_exception(
    request: Request, exception: ActiveCartException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(ExceededItemQuantityException)
def handle_exceeded_item_quantity_exception(
    request: Request, exception: ExceededItemQuantityException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )

@app.exception_handler(NonPositiveCartItemQuantityException)
def handle_non_positive_cart_item_quantity_exception(
    request: Request, exception: NonPositiveCartItemQuantityException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    ) 


@app.exception_handler(EmptyCartException)
def handle_empty_cart_exception(
    request: Request, exception: EmptyCartException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    ) 
    
@app.exception_handler(NoSuchItemInCartException)
def handle_no_such_item_in_cart_exception(
    request: Request, exception: NoSuchItemInCartException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    ) 
    
@app.exception_handler(QuantityLowerThanAmountOfProductItemsInCartsException)
def handle_quantity_lower_than_item_in_carts_amount_exception(
    request: Request, exception: QuantityLowerThanAmountOfProductItemsInCartsException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    ) 