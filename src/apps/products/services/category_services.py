from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    CategoryInputSchema,
    CategoryOutputSchema,
    ProductInputSchema,
    ProductOutputSchema,
    ProductAddInputSchema
)
from src.apps.products.models import Category, Product
from src.apps.products.exceptions import (category_already_exists_exception,
    category_does_not_exist_exception,
    category_name_is_occupied_exception
)


def create_category(session: Session, category: CategoryInputSchema) -> CategoryOutputSchema:
    category_data = category.dict()

    category_name_check = session.scalar(select(Category).filter(Category.name == category_data["name"]).limit(1))
    if category_name_check:
        raise category_name_is_occupied_exception

    new_category = Category(**category_data)
    session.add(new_category)
    session.commit()

    return CategoryOutputSchema.from_orm(new_category)

def get_single_category(session: Session, category_id: int) -> CategoryOutputSchema:
    category_object = session.scalar(select(Category).filter(Category.id==category_id).limit(1))
    if not category_object:
        raise category_does_not_exist_exception

    return CategoryOutputSchema.from_orm(category_object)

def get_all_categories(session: Session) -> list[CategoryOutputSchema]:
    instances = session.scalars(select(Category))

    return [CategoryOutputSchema.from_orm(instance) for instance in instances]

def update_single_category(session: Session, category: CategoryInputSchema, category_id: int) -> CategoryOutputSchema:
    category_object = session.scalar(select(Category).filter(Category.id==category_id).limit(1))
    if not category_object:
        raise category_does_not_exist_exception
    
    category_name_check = session.scalar(select(Category).filter(Category.name == category.name).limit(1))
    if category_name_check.first():
        raise category_name_is_occupied_exception

    statement = update(Category).filter(Category.id == category_id).values(**category.dict())

    session.execute(statement)
    session.commit()
    
    return get_single_category(session, category_id=category_id)

def delete_single_category(session: Session, category_id: int):
    category_object = session.scalar(select(Category).filter(Category.id==category_id).limit(1))
    if not category_object:
        category_does_not_exist_exception

    statement = delete(Category).filter(Category.id == category_id)
    result = session.execute(statement)
    session.commit()

    return result
