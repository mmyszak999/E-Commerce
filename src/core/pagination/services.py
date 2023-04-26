from sqlalchemy import func, Table, select
from sqlalchemy.orm import Session

from src.core.pagination.models import BaseModel, PageParams, conint
from src.core.pagination.schemas import PagedResponseSchema, T

def paginate(
    query, response_schema: BaseModel, table: Table, page_params: PageParams, session: Session
    ) -> PagedResponseSchema[T]:
    results = session.scalars(query.offset((page_params.page - 1) * page_params.size).limit(page_params.size)).all()
    
    return PagedResponseSchema(
        total=session.scalar(select(func.count()).select_from(table)),
        page=page_params.page,
        size=page_params.size,
        results=[response_schema.from_orm(item) for item in paginated_query],
        has_next_page=len(results) > page_params.size
    )
