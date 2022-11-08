from fastapi import FastAPI, APIRouter

from src.apps.user.routers.user import router


app = FastAPI()

root_router = APIRouter(prefix="/api")

root_router.include_router(router)

app.include_router(root_router)
