import copy
from typing import Any
from datetime import datetime, timedelta

import pytest
from pydantic.error_wrappers import ValidationError

from src.apps.user.schemas import UserRegisterSchema
from src.core.factories import UserFactory

@pytest.mark.parametrize('incorrect_password', 'passwordX')
def test_passwords_are_not_identical(incorrect_password):
    with pytest.raises(ValidationError):
        user_data = UserFactory.build(password="password", password_repeat=incorrect_password)
        UserRegisterSchema(**user_data)
        
@pytest.mark.parametrize('future_date', [datetime.now() + timedelta(days=1)])
def test_date_is_from_future(future_date):
    with pytest.raises(ValidationError):
        user_data = UserFactory.build(birth_date=future_date, password="password", password_repeat="password")
        UserRegisterSchema(**user_data)






    



