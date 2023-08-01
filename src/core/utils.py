from typing import Any

from sqlalchemy import Table, select, desc, asc
from sqlalchemy.orm import Session

from src.core.exceptions import ServiceException


def if_exists(model_class: Table, field: str, value: Any, session: Session) -> bool:
    return session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )


def check_if_request_user(
    request_user_attr: Any, resource_owner_attrib: Any, message: str
) -> None:
    if request_user_attr != resource_owner_attrib:
        raise ServiceException(message)


def filter_query_param_values_extractor(params_list):
    desired_params_list = [param for param in params_list if not param[0] == 'sort']
    for param in desired_params_list:
        key, value = param
        try:
            field, oper = key.split("__")
        except:
            field = key
            oper = "eq"
        yield field, oper, value
        

def sort_query_param_values_extractor(params_list: list[tuple], model_class: Table) -> dict[Any, str]:
    params = [param for param in params_list if param[0] == 'sort']
    criteria = dict()
    if params:
        for criterion in params[0][1].split(','):
            field, sorting_order = criterion.split('__')
            field = getattr(model_class, field)
            criteria[field] = sorting_order
        return criteria
        



