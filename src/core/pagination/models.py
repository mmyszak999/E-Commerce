from typing import TypeVar
from pydantic import BaseModel, conint


class PageParams(BaseModel):
    page: conint(ge=1) = 1
    size: conint(ge=1, le=100) = 10
