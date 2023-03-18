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
from src.apps.products.services.category_services import get_single_category


def create_product(session: Session, product: ProductInputSchema) -> ProductOutputSchema:
    product_data = product.dict()

    name_check = session.execute(select(Product).filter(Product.name == product_data["name"]))
    if name_check:
        pass
    
    categories = product_data.pop('categories')
    product_data['categories'] = [
        session.scalar(select(Category).filter(Category.id == instance["id"])) for instance in categories
        ]
    new_product = Product(**product_data)
    session.add(new_product)
    session.commit()

    return ProductOutputSchema.from_orm(new_product)

def get_single_product(session: Session, product_id: int) -> ProductOutputSchema:
    statement = select(Product).filter(Product.id == product_id).limit(1)
    if session.scalar(statement) is None:
        pass

    instance = session.execute(statement).scalar()
    return ProductOutputSchema.from_orm(instance)

def get_all_products(session: Session) -> list[ProductOutputSchema]:
    statement = select(Product)
    instances = session.execute(statement).scalars()

    return [ProductOutputSchema.from_orm(instance) for instance in instances]

def update_single_product(session: Session, product: ProductInputSchema, product_id: int):
    if_exists = select(Product.id).filter(Product.id == product_id)
    searched_product = session.scalar(if_exists)
    if searched_product is None:
        pass
    
    name_check = session.execute(select(Product).filter(Product.name == product.name))
    if name_check.first():
        pass
    
    product_data = product.dict()

    categories = product_data.pop('categories')
    product_data['categories'] = [
        session.scalar(select(Category).filter(Category.id == instance["id"])) for instance in categories
        ]
    statement = update(Product).filter(Product.id == product_id).values(**product_data)

    session.execute(statement)
    session.commit()
    
    return get_single_product(session, product_id=product_id)

def delete_single_product(session: Session, product_id: int):
    if_exists = select(Product).filter(Product.id == product_id)
    if session.scalar(if_exists) is None:
        pass

    statement = delete(Product).filter(Product.id == product_id)
    result = session.execute(statement)
    session.commit()

    return result
