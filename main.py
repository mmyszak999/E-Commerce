from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from src.apps.jwt.routers import jwt_router
from src.apps.orders.routers import order_router
from src.apps.products.routers import category_router, product_router
from src.apps.orders.routers import order_router
from src.apps.emails.routers import email_router
from src.apps.user.routers import user_router
from src.apps.admin.routers import admin_router
from src.core.exceptions import (
    AlreadyExists,
    AuthenticationException,
    AuthorizationException,
    DoesNotExist,
    IsOccupied,
    ServiceException,
)

app = FastAPI()

root_router = APIRouter(prefix="/api")

root_router.include_router(user_router)
root_router.include_router(jwt_router)
root_router.include_router(category_router)
root_router.include_router(product_router)
root_router.include_router(order_router)
root_router.include_router(email_router)
root_router.include_router(admin_router)

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
