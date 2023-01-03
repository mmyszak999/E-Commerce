from fastapi import HTTPException


class UserDoesNotExistException(Exception):
    pass

class UserAlreadyExists(Exception):
    pass

class FieldNameIsOccupied(Exception):
    pass

class AuthException(HTTPException):
    pass