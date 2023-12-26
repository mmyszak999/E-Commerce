from typing import Any


class Sort:
    def __init__(self, main_model, inst, current_model=None):
        self.main_model = main_model
        self.inst = inst
        self.sort_params = None
        self.current_model = current_model

    def set_sort_params(self, query_params: list[tuple]) -> None:
        from src.core.utils import sort_query_param_values_extractor

        self.sort_params = sort_query_param_values_extractor(query_params, self.current_model)

    def get_sorted_instances(self):
        from src.core.utils import check_relationships
        
        if self.sort_params:
            for field, sort_order in self.sort_params.items():
                print(field, sort_order)
                if len(field.split("__")) == 1:
                    self.current_model = self.main_model
                else:
                    key, field = field.split("__")
                    self.current_model = check_relationships(self.main_model, key)

            field = getattr(self.current_model, field)
            statement = field.asc() if sort_order == "asc" else field.desc()
            self.inst = self.inst.order_by(statement)
        return self.inst
