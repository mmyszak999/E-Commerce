from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.apps.user.models.user import User
from src.apps.user.schemas.user import UserRegisterSchema, UserUpdateSchema

