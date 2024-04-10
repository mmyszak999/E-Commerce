from typing import Union

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session, joinedload

from src.apps.orders.models import CartItem

# from src.apps.orders.services.cart_items_services import ...
from src.apps.products.models import (
    Category,
    Product,
    ProductInventory,
    category_product_association_table,
)
from src.apps.products.schemas import (
    InventoryOutputSchema,
    InventoryUpdateSchema,
    ProductInputSchema,
    ProductOutputSchema,
    ProductUpdateSchema,
)
from src.apps.products.services.inventory_services import update_single_inventory
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import filter_and_sort_instances, if_exists


def create_product(
    session: Session, product: ProductInputSchema
) -> ProductOutputSchema:
    product_data = product.dict()

    if product_data.get("name"):
        name_check = session.scalar(
            select(Product).filter(Product.name == product_data["name"]).limit(1)
        )
        if name_check:
            raise AlreadyExists(Product.__name__, "name", product.name)

    if category_ids := product_data.pop("category_ids"):
        categories = session.scalars(
            select(Category).where(Category.id.in_(category_ids))
        ).all()
        if not len(set(category_ids)) == len(categories):
            raise ServiceException("Wrong categories!")

        product_data["categories"] = categories

    if product_data.get("inventory"):
        inventory_data = product_data.pop("inventory")

    new_product = Product(**product_data)

    session.add(new_product)
    session.commit()

    new_inventory = ProductInventory(
        quantity=inventory_data["quantity"],
        quantity_for_cart_items=inventory_data["quantity"],
        product_id=new_product.id,
    )
    session.add(new_inventory)
    session.commit()

    return ProductOutputSchema.from_orm(new_product)


def get_single_product_or_inventory(
    session: Session, product_id: str, get_inventory=False
) -> Union[ProductOutputSchema, InventoryOutputSchema]:
    if not (product_object := if_exists(Product, "id", product_id, session)):
        raise DoesNotExist(Product.__name__, "id", product_id)

    if not get_inventory:
        return ProductOutputSchema.from_orm(product_object)
    return InventoryOutputSchema.from_orm(product_object.inventory)


def get_all_products(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema:
    query = (
        select(Product)
        .join(
            category_product_association_table,
            Product.id == category_product_association_table.c.product_id,
        )
        .join(
            Category,
            category_product_association_table.c.category_id == Category.id,
            isouter=True,
        )
    )

    if query_params:
        query = filter_and_sort_instances(query_params, query, Product)

    return paginate(
        query=query,
        response_schema=ProductOutputSchema,
        table=Product,
        page_params=page_params,
        session=session,
    )


def update_single_product(
    session: Session, product_input: ProductUpdateSchema, product_id: str
) -> ProductOutputSchema:
    if not (product_object := if_exists(Product, "id", product_id, session)):
        raise DoesNotExist(Product.__name__, "id", product_id)

    product_data = product_input.dict(exclude_unset=True, exclude_none=True)

    if product_data.get("name"):
        product_name_check = session.scalar(
            select(Product).filter(Product.name == product_input.name).limit(1)
        )
        if product_name_check and (product_name_check.id != product_id):
            raise IsOccupied(Product.__name__, "name", product_input.name)

    if (new_product_price := product_data.get("price")) and (
        product_data.get("price") != product_object.price
    ):
        cart_items = session.scalars(
            select(CartItem).filter(CartItem.product_id == product_object.id)
        )
        rows = [
            {
                "id": cart_item.id,
                "cart_item_price": float(new_product_price) * cart_item.quantity,
            }
            for cart_item in cart_items
        ]

        session.execute(update(CartItem), rows)

    if product_data.get("category_ids"):
        incoming_categories = set(product_data["category_ids"])
        current_categories = set(category.id for category in product_object.categories)

        if to_delete := current_categories - incoming_categories:
            session.execute(
                delete(category_product_association_table).where(
                    Category.id.in_(to_delete)
                )
            )

        if to_insert := incoming_categories - current_categories:
            rows = [
                {"product_id": product_id, "category_id": category_id}
                for category_id in to_insert
            ]
            session.execute(insert(category_product_association_table).values(rows))

        product_data.pop("category_ids")

    if "inventory" in product_data.keys():
        if product_data.get("inventory"):
            inventory_data = product_data.pop("inventory")
            update_single_inventory(
                session,
                InventoryUpdateSchema(**inventory_data),
                product_object.inventory.id,
            )

        else:
            product_data.pop("inventory")

    if product_data:
        statement = (
            update(Product).filter(Product.id == product_id).values(**product_data)
        )

        session.execute(statement)
        session.commit()
        session.refresh(product_object)

    return get_single_product_or_inventory(session, product_id=product_id)


def delete_single_product(session: Session, product_id: str):
    if not if_exists(Product, "id", product_id, session):
        raise DoesNotExist(Product.__name__, "id", product_id)

    statement = delete(Product).filter(Product.id == product_id)
    result = session.execute(statement)
    session.commit()

    return result
