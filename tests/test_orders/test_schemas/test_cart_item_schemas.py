from contextlib import nullcontext as does_not_raise
from datetime import datetime, timedelta

import pytest
from pydantic.error_wrappers import ValidationError

from src.core.factories import CartItemInputSchemaFactory, CartItemUpdateSchemaFactory
from src.core.utils.utils import generate_uuid


@pytest.mark.parametrize(
    "quantity, result",
    [
        (2, does_not_raise()),
        (-2, pytest.raises(ValidationError)),
    ],
)
def test_cart_item_input_schema_raises_validation_error_when_quantity_is_negative(
    quantity, result
):
    with result:
        CartItemInputSchemaFactory().generate(
            generate_uuid(),
            quantity=quantity,
        )

    with result:
        CartItemUpdateSchemaFactory().generate(
            quantity=quantity,
        )
