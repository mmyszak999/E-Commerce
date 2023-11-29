from random import randint
from typing import Any

from faker import Faker
from faker.providers import date_time, internet, misc, person
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from itsdangerous import URLSafeTimedSerializer
from pydantic import BaseModel, BaseSettings
from sqlalchemy import Table, select
from sqlalchemy.orm import Session

from src.core.exceptions import ServiceException
from src.core.sort import Sort
from src.core.filters import Lookup
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
    desired_params_list = [param for param in params_list if not param[0] in ["sort", "page", "size"]]
    for param in desired_params_list:
        key, value = param
        try:
            field, oper = key.split("__")
        except Exception:
            field = key
            oper = "eq"
        yield field, oper, value


def sort_query_param_values_extractor(
    params_list: list[tuple], model_class: Table
) -> dict[Any, str]:
    params = [param for param in params_list if param[0] == "sort"]
    criteria = dict()
    if params:
        for criterion in params[0][1].split(","):
            field, sorting_order = criterion.split("__")
            field = getattr(model_class, field)
            criteria[field] = sorting_order
        return criteria
    

def filter_instances(query_params: list[tuple], instances, model):
    filter_class = Lookup(model, instances)
    filter_params = filter_query_param_values_extractor(query_params)
    for param in filter_params:
        instances = filter_class.perform_lookup(*param)
    return instances.inst    


def sort_instances(query_params: list[tuple], instances, model):
    sort = Sort(model, instances)
    sort.set_sort_params(query_params)
    sort.get_sorted_instances()
    return sort.inst
    
    
def filter_and_sort_instances(query_params: list[tuple], instances, model):
    params_keys = [param[0] for param in query_params]
    pagination_keys = [param for param in params_keys if param in ['page', 'size']]
    if pagination_keys == params_keys:
        return instances
    
    [params_keys.remove(value) for value in pagination_keys]
    check_if_sort_key = 'sort' in params_keys
    filter_keys = [param for param in params_keys if param != 'sort']
    if filter_keys:
        instances = filter_instances(query_params, instances, model)

    if check_if_sort_key:
        instances = sort_instances(query_params, instances, model)
    
    return instances


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
