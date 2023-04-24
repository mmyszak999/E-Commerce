from typing import Generic, List
from pydantic.generics import GenericModel

from src.core.pagination.models import T


class PagedResponseSchema(GenericModel, Generic[T]):
    total: int
    page: int
    size: int
    results: List[T]
