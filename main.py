from fastapi import FastAPI, APIRouter

from src.apps.user.database import engine
from src.apps.user.routers.routers import router
from src.apps.user.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

root_router = APIRouter(prefix="/api")

root_router.include_router(router)

app.include_router(root_router)
