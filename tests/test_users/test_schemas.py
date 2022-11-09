from typing import Any

import pytest
from pydantic.error_wrappers import ValidationError

from src.apps.user.schemas.user import UserRegisterSchema

def test_passwords_are_not_identical(
    incorrect_passwords_dict: dict[str, Any]
):
    with pytest.raises(ValidationError) as exc:
        UserRegisterSchema(**incorrect_passwords_dict)


def test_date_is_from_future(
    date_from_future_dict: dict[str, Any]
):
    with pytest.raises(ValidationError) as exc:
        UserRegisterSchema(**date_from_future_dict)






    



