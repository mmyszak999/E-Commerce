import datetime
import uuid
from decimal import Decimal
from random import randint
from typing import Any

from faker import Faker
from faker.providers import address, date_time, internet, lorem, misc, person
from faker_commerce import Provider as commerce_provider
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from itsdangerous import URLSafeTimedSerializer
from pydantic import BaseModel, BaseSettings
from sqlalchemy import Table, select
from sqlalchemy.orm import Session, class_mapper
from sqlalchemy.orm.properties import RelationshipProperty

from src.core.exceptions import ServiceException
from src.core.filters import Lookup
from src.core.sort import Sort
from src.core.utils.constants import (
    PAGINATION_PARAMS_HEADERS,
    PARAM_HEADERS_WITHOUT_FILTERS,
    SORT_PARAMS_HEADER,
)
from src.database.db_connection import Base
from src.settings.general import settings


def if_exists(model_class: Table, field: str, value: Any, session: Session):
    return session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )


def initialize_faker():
    faker = Faker("en_US")
    faker.seed_instance(randint(1, 1000))
    faker.add_provider(person)
    faker.add_provider(internet)
    faker.add_provider(date_time)
    faker.add_provider(misc)
    faker.add_provider(commerce_provider)
    faker.add_provider(address)
    faker.add_provider(lorem)

    return faker


def generate_confirm_token(objects: list[str]) -> str:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(objects, salt=settings.SECURITY_PASSWORD_SALT)


def confirm_token(token: str, expiration=3600) -> list[str]:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        objects = serializer.loads(
            token, salt=settings.SECURITY_PASSWORD_SALT, max_age=expiration
        )
        return objects

    except Exception:
        return False


def check_field_values(
    request_user_attr: Any, resource_owner_attrib: Any, message: str
) -> None:
    if request_user_attr != resource_owner_attrib:
        raise ServiceException(message)


def filter_query_param_values_extractor(params_list):
    desired_params_list = [
        param for param in params_list if param[0] not in PARAM_HEADERS_WITHOUT_FILTERS
    ]
    for param in desired_params_list:
        key, value = param
        try:
            field, oper = key.rsplit("__", 1)
        except Exception:
            field = key
            oper = "eq"
        yield field, oper, value


def sort_query_param_values_extractor(
    params_list: list[tuple], model_class: Table
) -> dict[Any, str]:
    params = [param for param in params_list if param[0] == SORT_PARAMS_HEADER]
    criteria = dict()
    if params:
        for criterion in params[0][1].split(","):
            field, sorting_order = criterion.rsplit("__", 1)
            criteria[field] = sorting_order
        return criteria


def filter_instances(query_params: list[tuple], instances, model):
    filter_class = Lookup(model, instances)
    filter_class.set_filter_params(query_params)
    filter_class.get_filtered_instances()
    return filter_class.inst


def sort_instances(query_params: list[tuple], instances, model):
    sort_class = Sort(model, instances)
    sort_class.set_sort_params(query_params)
    sort_class.get_sorted_instances()
    return sort_class.inst


def filter_and_sort_instances(query_params: list[tuple], instances, model):
    params_keys = [param[0] for param in query_params]
    pagination_keys = [
        param for param in params_keys if param in PAGINATION_PARAMS_HEADERS
    ]
    if pagination_keys == params_keys:
        return instances

    [params_keys.remove(value) for value in pagination_keys]
    check_if_sort_key = SORT_PARAMS_HEADER in params_keys
    filter_keys = [param for param in params_keys if param != SORT_PARAMS_HEADER]
    if filter_keys:
        instances = filter_instances(query_params, instances, model)

    if check_if_sort_key:
        instances = sort_instances(query_params, instances, model)

    return instances


def get_model_from_key_name(model, relationship_key: str):
    mapper = class_mapper(model)
    for property in mapper.iterate_properties:
        if (
            isinstance(property, RelationshipProperty)
            and property.key == relationship_key
        ):
            for klass in Base.__subclasses__():
                if klass.__tablename__ == property.target.name:
                    return klass


def send_email(
    schema: BaseModel,
    body_schema: BaseModel,
    background_tasks: BackgroundTasks,
    settings: BaseSettings,
) -> None:
    email_message = MessageSchema(
        subject=schema.email_subject,
        recipients=schema.receivers,
        template_body=body_schema.dict(),
        subtype="html",
    )

    fast_mail = FastMail(settings)
    background_tasks.add_task(
        fast_mail.send_message, email_message, template_name=schema.template_name
    )


def generate_uuid():
    return str(uuid.uuid4())


def calculate_item_price(quantity: int, product_price: Decimal) -> Decimal:
    return quantity * product_price


def validate_item_quantity(product_quantity: int, entered_quantity: int) -> bool:
    return entered_quantity <= product_quantity


def get_current_time():
    return datetime.datetime.now()


def set_cart_item_validity():
    return get_current_time() + datetime.timedelta(minutes=30)


def set_payment_deadline():
    return get_current_time() + datetime.timedelta(minutes=60)
