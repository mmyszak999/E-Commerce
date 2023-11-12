from typing import Any

from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import Table, select
from sqlalchemy.orm import Session

from src.core.exceptions import ServiceException
from src.settings.general import settings


def if_exists(model_class: Table, field: str, value: Any, session: Session):
    return session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )
    
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
    desired_params_list = [param for param in params_list if not param[0] == "sort"]
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
