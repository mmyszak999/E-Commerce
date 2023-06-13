import copy
from typing import Any
from datetime import datetime, timedelta

import pytest
from pydantic.error_wrappers import ValidationError

from src.apps.user.schemas import UserRegisterSchema
from src.core.factories import UserFactory

def test_passwords_are_not_identical():
    with pytest.raises(ValidationError):
        user_data = UserFactory.build(password="password", password_repeat="passwordX")
        UserRegisterSchema(**user_data)

def test_date_is_from_future():
    with pytest.raises(ValidationError):
        future_date = datetime.now()+timedelta(days=1)
        user_data = UserFactory.build(birth_date=future_date, password="password", password_repeat="password")
        UserRegisterSchema(**user_data)






    



