import copy
from typing import Any
from datetime import datetime, timedelta
from contextlib import nullcontext as does_not_raise

import pytest
from pydantic.error_wrappers import ValidationError

from src.apps.user.schemas import UserRegisterSchema
from src.core.factories import UserRegisterSchemaFactory

@pytest.mark.parametrize(
    "password1, password2, result",
    [("testtest1", "testtest1", does_not_raise()), ("testtest1", "testtest2", pytest.raises(ValidationError))]
)
def test_user_register_schema_raises_validation_error_when_passwords_are_not_identical(password1, password2, result):
    with result:
        UserRegisterSchemaFactory.build(password=password1, password_repeat=password2)
        
@pytest.mark.parametrize(
    "future_date, result",
    [(datetime.now() - timedelta(days=1), does_not_raise()),
     (datetime.now() + timedelta(days=1), pytest.raises(ValidationError))]
)
def test_user_register_schema_raises_validation_error_when_birth_date_is_from_future(future_date, result):
    with result:
        UserRegisterSchemaFactory.build(birth_date=future_date, password="password", password_repeat="password")






    



