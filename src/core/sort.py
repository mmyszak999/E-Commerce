from typing import Any

from sqlalchemy import asc, desc

from src.core.utils import sort_query_param_values_extractor


class Sort:
    def __init__(self, model, inst):
        self.model = model
        self.inst = inst
        self.sort_params = None

    def set_sort_params(self, query_params: list[tuple]) -> dict[Any, str]:
        self.sort_params = sort_query_param_values_extractor(query_params, self.model)

    def get_sorted_instances(self):
        if self.sort_params:
            for field, sort_order in self.sort_params.items():
                statement = field.asc() if sort_order == "asc" else field.desc()
                self.inst = self.inst.order_by(statement)
            return self.inst
