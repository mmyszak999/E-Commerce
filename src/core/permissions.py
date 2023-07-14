from src.apps.user.models import User
from src.core.exceptions import AuthorizationException


def check_permission(request_user: User) -> None:
    if not request_user.is_superuser:
        raise AuthorizationException("You don't have superuser permission to access the group of resources")


def check_object_permission(user_id: int, request_user: User) -> None:
    if not(request_user.is_superuser or request_user.id == user_id):
        raise AuthorizationException("You don't have permission to access the resource")