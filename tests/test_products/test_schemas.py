import pytest
from pydantic.error_wrappers import ValidationError

from src.core.factories import InventoryInputSchemaFactory


def test_inventory_input_schema_raises_validation_error_when_quantity_is_negative():
    with pytest.raises(ValidationError) as exc:
        InventoryInputSchemaFactory().generate(-21)
