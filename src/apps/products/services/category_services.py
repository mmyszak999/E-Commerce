from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.apps.products.models import Category
from src.apps.products.schemas import CategoryInputSchema, CategoryOutputSchema
from src.core.exceptions import AlreadyExists, DoesNotExist, IsOccupied
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils import (
    filter_and_sort_instances,
    filter_query_param_values_extractor,
    if_exists,
)


def create_category(
    session: Session, category: CategoryInputSchema
) -> CategoryOutputSchema:
    category_data = category.dict()

    if category_data:
        category_name_check = session.scalar(
            select(Category).filter(Category.name == category_data["name"]).limit(1)
        )
        if category_name_check:
            raise AlreadyExists(Category.__name__, "name", category.name)

    new_category = Category(**category_data)
    session.add(new_category)
    session.commit()

    return CategoryOutputSchema.from_orm(new_category)


def get_single_category(session: Session, category_id: int) -> CategoryOutputSchema:
    if not (category_object := if_exists(Category, "id", category_id, session)):
        raise DoesNotExist(Category.__name__, "id", category_id)

    return CategoryOutputSchema.from_orm(category_object)


def get_all_categories(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[CategoryOutputSchema]:
    query = select(Category)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Category)

    return paginate(
        query=query,
        response_schema=CategoryOutputSchema,
        table=Category,
        page_params=page_params,
        session=session,
    )


def update_single_category(
    session: Session, category_input: CategoryInputSchema, category_id: int
) -> CategoryOutputSchema:
    if not if_exists(Category, "id", category_id, session):
        raise DoesNotExist(Category.__name__, "id", category_id)

    category_data = category_input.dict(exclude_unset=True)

    if category_data:
        category_name_check = session.scalar(
            select(Category).filter(Category.name == category_input.name).limit(1)
        )
        if category_name_check:
            raise IsOccupied(Category.__name__, "name", category_input.name)

        statement = (
            update(Category).filter(Category.id == category_id).values(**category_data)
        )

        session.execute(statement)
        session.commit()

    return get_single_category(session, category_id=category_id)


def delete_single_category(session: Session, category_id: int):
    if not if_exists(Category, "id", category_id, session):
        raise DoesNotExist(Category.__name__, "id", category_id)

    statement = delete(Category).filter(Category.id == category_id)
    result = session.execute(statement)
    session.commit()

    return result
