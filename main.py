from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from src.apps.user.routers import router
from src.apps.jwt.routers import jwt_router
from src.apps.products.routers import product_router


app = FastAPI()

root_router = APIRouter(prefix="/api")

root_router.include_router(router)
root_router.include_router(jwt_router)
root_router.include_router(product_router)

app.include_router(root_router)


@app.exception_handler(AuthJWTException)
def auth_jwt_exception_handler(request: Request, exception: AuthJWTException) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exception.message})
