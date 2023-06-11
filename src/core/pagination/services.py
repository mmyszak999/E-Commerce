from sqlalchemy import func, Table, select
from sqlalchemy.orm import Session

from src.core.pagination.models import BaseModel, PageParams, conint
from src.core.pagination.schemas import PagedResponseSchema, T


def paginate(
    query, response_schema: BaseModel, table: Table, page_params: PageParams, session: Session
    ) -> PagedResponseSchema[T]:
    instances = session.scalars(query.offset((page_params.page - 1) * page_params.size).limit(page_params.size + 1)).all()
    next_page_check = len(instances) > page_params.size
    
    return PagedResponseSchema(
        page=page_params.page,
        size=page_params.size,
        results=[response_schema.from_orm(item) for item in instances[:page_params.size]],
        has_next_page=next_page_check
    )