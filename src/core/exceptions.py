from typing import Any


class ServiceException(Exception):
    pass


class DoesNotExist(ServiceException):
    def __init__(self, class_name: str, _id: int) -> None:
        super().__init__(f"{class_name} with id={_id} does not exist")


class AlreadyExists(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{class_name} with {field}={value} already exists")


class IsOccupied(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{field}={value} value of {class_name} is occupied")


class AuthenticationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class AuthorizationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")
