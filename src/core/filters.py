import operator

from sqlalchemy import select
from sqlalchemy.sql.expression import Select

from src.apps.products.models import Product


class Lookup(Select):
    def __init__(self, model, inst, current_model=None):
        self.main_model = model
        self.inst = inst
        self.current_model = current_model
        self.field = None
        self.filter_params = None

    def __lt__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) < other)

    def __gt__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) > other)

    def __ge__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) >= other)

    def __le__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) <= other)

    def __eq__(self, other):
        values = other.split(",")
        if len(values) > 1:
            return self.inst.filter(getattr(self.current_model, self.field).in_(values))
        return self.inst.filter(getattr(self.current_model, self.field) == other)

    def __ne__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) != other)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def set_filter_params(self, query_params: list[tuple]) -> None:
        from src.core.utils.utils import filter_query_param_values_extractor

        self.filter_params = filter_query_param_values_extractor(query_params)

    def perform_lookup(self, field, operation, value):
        from src.core.utils.utils import get_model_from_key_name

        if len(field.split("__")) == 1:
            self.field = field
            self.current_model = self.main_model
        else:
            key, self.field = field.split("__")
            self.current_model = get_model_from_key_name(self.main_model, key)

        res = getattr(operator, operation)(self, value)
        return Lookup(self.main_model, res, self.current_model)

    def get_filtered_instances(self):
        for param in self.filter_params:
            self.inst = self.perform_lookup(*param).inst
        return self.inst
