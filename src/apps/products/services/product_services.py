from sqlalchemy import delete, select, update, insert
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    CategoryInputSchema,
    CategoryOutputSchema,
    ProductInputSchema,
    ProductOutputSchema,
    ProductAddInputSchema
)
from src.apps.products.models import Category, Product, association_table
from src.apps.products.services.category_services import get_single_category
from src.apps.products.exceptions import (
    product_already_exists_exception,
    product_does_not_exist_exception,
    product_name_is_occupied_exception
)


def create_product(session: Session, product: ProductInputSchema) -> ProductOutputSchema:
    product_data = product.dict()

    name_check = session.scalar(select(Product).filter(Product.name == product_data["name"]).limit(1))
    print("w", name_check)
    if name_check:
        raise product_name_is_occupied_exception
    
    categories = product_data.pop('categories')
    product_data['categories'] = [
        session.scalar(select(Category).filter(Category.id == instance["id"])) for instance in categories
        ]
    new_product = Product(**product_data)
    session.add(new_product)
    session.commit()

    return ProductOutputSchema.from_orm(new_product)

def get_single_product(session: Session, product_id: int) -> ProductOutputSchema:
    product_object = session.execute(select(Product).filter(Product.id==product_id)).scalar()
    if not product_object:
        raise product_does_not_exist_exception

    instance = session.execute(statement).scalar()
    return ProductOutputSchema.from_orm(instance)

def get_all_products(session: Session) -> list[ProductOutputSchema]:
    instances = session.execute(select(Product)).scalars()

    return [ProductOutputSchema.from_orm(instance) for instance in instances]

def update_single_product(session: Session, product: ProductInputSchema, product_id: int) -> ProductOutputSchema:
    product_object = session.execute(select(Product).filter(Product.id==product_id)).scalar()
    if not product_object:
        raise product_does_not_exist_exception
    
    product_name_check = session.execute(select(Product).filter(Product.name == product.name))
    if product_name_check.first():
        raise product_name_is_occupied_exception
    
    product_data = product.dict()
    incoming_categories = set(category['id'] for category in product_data['categories'])
    current_categories = set(category.id for category in product_object.categories)

    disjoint_categories_id_set = incoming_categories ^ current_categories

    rows = [{"product_id": product_id, "category_id": category_id} for category_id in disjoint_categories_id_set if category_id in current_categories]
    if rows:
        session.execute(delete(association_table).where(Category.id.in_([row['category_id'] for row in rows])))

    rows = [{"product_id": product_id, "category_id": category_id} for category_id in disjoint_categories_id_set if category_id in incoming_categories]
    if rows:
        session.execute(insert(association_table).values(rows))

    product_data.pop('categories')
    statement = update(Product).filter(Product.id==product_id).values(**product_data)
    
    session.execute(statement)
    session.commit()
    session.refresh(product_object)
    
    return get_single_product(session, product_id=product_id)

def delete_single_product(session: Session, product_id: int):
    product_object = session.execute(select(Product).filter(Product.id==product_id)).scalar()
    if not product_object:
        raise product_does_not_exist_exception

    statement = delete(Product).filter(Product.id == product_id)
    result = session.execute(statement)
    session.commit()

    return result
