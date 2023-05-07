from typing import Any
from datetime import date

import pytest
from pydantic.error_wrappers import ValidationError

from src.apps.user.schemas import UserRegisterSchema



def test_passwords_are_not_identical(
    register_data: dict[str, Any]
):
    user_data = register_data
    user_data['password_repeat'] = user_data['password'] + "abcde"
    with pytest.raises(ValidationError) as exc:
        UserRegisterSchema(**user_data)

def test_date_is_from_future(
    register_data: dict[str, Any]
):
    user_data = register_data
    user_data['birth_date'] = '9922-02-12'
    with pytest.raises(ValidationError) as exc:
        UserRegisterSchema(**user_data)






    



