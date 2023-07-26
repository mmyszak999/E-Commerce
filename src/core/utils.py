from typing import Any

from sqlalchemy import Table, select
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
