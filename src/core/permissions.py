from src.apps.user.models import User
from src.core.exceptions import AuthorizationException


def check_if_superuser(request_user: User) -> None:
    if not request_user.is_superuser:
        raise AuthorizationException(
            "You don't have superuser permissions to perform this action!"
        )


def check_if_staff(request_user: User) -> None:
    if not request_user.is_staff:
        raise AuthorizationException(
            "You don't have staff permissions to perform this action!"
        )


def check_if_staff_or_owner(request_user: User, user_id: int) -> None:
    if not (request_user.is_superuser or request_user.id == user_id):
        raise AuthorizationException("You don't have permissions to access the resource")
