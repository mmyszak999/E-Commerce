from fastapi import FastAPI, APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from src.apps.user.routers.user import router
from src.apps.user.routers.jwt import jwt_router


app = FastAPI()

root_router = APIRouter(prefix="/api")

root_router.include_router(router)
root_router.include_router(jwt_router)

app.include_router(root_router)


@app.exception_handler(AuthJWTException)
def auth_jwt_exception_handler(request: Request, exception: AuthJWTException) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exception.message})
