from sqlalchemy import delete, select, update, insert
from sqlalchemy.orm import Session

from src.apps.products.schemas import (
    CategoryInputSchema,
    CategoryOutputSchema,
    ProductInputSchema,
    ProductOutputSchema
)
from src.apps.products.models import Category, Product, association_table
from src.apps.products.services.category_services import get_single_category
from src.core.exceptions import (
    DoesNotExist,
    AlreadyExists,
    IsOccupied
)


def create_product(session: Session, product: ProductInputSchema) -> ProductOutputSchema:
    product_data = product.dict()

    name_check = session.scalar(select(Product).filter(Product.name == product_data["name"]).limit(1))
    if name_check:
        raise AlreadyExists(Product.__name__, "name", product.name)
    
    categories = product_data.pop('categories')
    product_data['categories'] = [
        session.scalar(select(Category).filter(Category.id == instance["id"]).limit(1)) for instance in categories
        ]
    new_product = Product(**product_data)
    session.add(new_product)
    session.commit()

    return ProductOutputSchema.from_orm(new_product)

def get_single_product(session: Session, product_id: int) -> ProductOutputSchema:
    product_object = session.scalar(select(Product).filter(Product.id==product_id).limit(1))
    if not product_object:
        raise DoesNotExist(Product.__name__, product_id)

    instance = session.scalar(statement)
    return ProductOutputSchema.from_orm(instance)

def get_all_products(session: Session) -> list[ProductOutputSchema]:
    instances = session.scalars(select(Product))

    return [ProductOutputSchema.from_orm(instance) for instance in instances]

def update_single_product(session: Session, product: ProductInputSchema, product_id: int) -> ProductOutputSchema:
    product_object = session.scalar(select(Product).filter(Product.id==product_id).limit(1))
    if not product_object:
        raise DoesNotExist(Product.__name__, product_id)
    
    product_name_check = session.execute(select(Product).filter(Product.name == product.name).limit(1))
    if product_name_check:
        raise IsOccupied(Product.__name__, "name", product.name)
    
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
    product_object = session.scalar(select(Product).filter(Product.id==product_id).limit(1))
    if not product_object:
        raise DoesNotExist(Product.__name__, product_id)

    statement = delete(Product).filter(Product.id == product_id)
    result = session.execute(statement)
    session.commit()

    return result
