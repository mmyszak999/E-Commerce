from typing import Any

from src.apps.user.models import User
from src.core.exceptions import AuthorizationException


def check_if_superuser(request_user: User) -> bool:
    if not request_user.is_superuser:
        raise AuthorizationException(
            "You don't have superuser permissions to perform this action!"
        )
    return True

def check_if_staff(request_user: User) -> bool:
    if not request_user.is_staff:
        raise AuthorizationException(
            "You don't have staff permissions to perform this action!"
        )
    return True


def check_if_staff_or_owner(request_user: User, attribute: str, value: Any) -> bool:
    if not (request_user.is_staff or getattr(request_user, attribute) == value):
        raise AuthorizationException(
            "You don't have permissions to access the resource"
        )
    return True

def check_if_owner(request_user: User, attribute: str, value: Any) -> bool:
    if not (getattr(request_user, attribute) == value):
        raise AuthorizationException(
            "You don't have permissions to access the resource"
        )
    return True


