from src.core.pagination.models import BaseModel, PageParams, T
from src.core.pagination.schemas import PagedResponseSchema


def paginate(page_params: PageParams, query, ResponseSchema: BaseModel) -> PagedResponseSchema[T]:
    paginated_query = query.offset((page_params.page - 1) * page_params.size).limit(page_params.size).all()

    return PagedResponseSchema(
        total=query.count(),
        page=page_params.page,
        size=page_params.size,
        results=[ResponseSchema.from_orm(item) for item in paginated_query],
    )
