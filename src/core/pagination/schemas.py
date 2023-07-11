from typing import Generic, List, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class PagedResponseSchema(GenericModel, Generic[T]):
    total: int
    page: int
    size: int
    results: List[T]
    has_next_page: bool
