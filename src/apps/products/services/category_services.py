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


def create_category(session: Session, category: CategoryInputSchema) -> CategoryOutputSchema:
    category_data = category.dict()

    name_check = session.execute(select(Category).filter(Category.name == category_data["name"]))
    if name_check:
        pass

    new_category = Category(**category_data)
    session.add(new_category)
    session.commit()

    return CategoryOutputSchema.from_orm(new_category)

def get_single_category(session: Session, category_id: int) -> CategoryOutputSchema:
    statement = select(Category).filter(Category.id == category_id).limit(1)
    if session.scalar(statement) is None:
        pass

    instance = session.execute(statement).scalar()
    return CategoryOutputSchema.from_orm(instance)

def get_all_categories(session: Session) -> list[CategoryOutputSchema]:
    statement = select(Category)
    instances = session.execute(statement).scalars()

    return [CategoryOutputSchema.from_orm(instance) for instance in instances]

def update_single_category(session: Session, category: CategoryInputSchema, category_id: int):
    if_exists = select(Category.id).filter(Category.id == category_id)
    searched_user = session.scalar(if_exists)
    if searched_user is None:
        pass
    
    name_check = session.execute(select(Category).filter(Category.name == category.name))
    if name_check.first():
        pass

    statement = update(Category).filter(Category.id == category_id).values(**category.dict())

    session.execute(statement)
    session.commit()
    
    return get_single_category(session, category_id=category_id)

def delete_single_category(session: Session, category_id: int):
    if_exists = select(Category).filter(Category.id == category_id)
    if session.scalar(if_exists) is None:
        pass

    statement = delete(Category).filter(Category.id == category_id)
    result = session.execute(statement)
    session.commit()

    return result
