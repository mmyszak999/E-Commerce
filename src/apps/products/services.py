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

def get_single_category
    



