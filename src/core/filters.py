import operator

from sqlalchemy.sql.expression import Select


class Lookup(Select):
    def __init__(self, model, inst):
        self.model = model
        self.inst = inst
        self.field = None
        self.filter_params = None

    def __lt__(self, other):
        return self.inst.filter(getattr(self.model, self.field) < other)

    def __gt__(self, other):
        return self.inst.filter(getattr(self.model, self.field) > other)

    def __ge__(self, other):
        return self.inst.filter(getattr(self.model, self.field) >= other)

    def __le__(self, other):
        return self.inst.filter(getattr(self.model, self.field) <= other)

    def __eq__(self, other):
        return self.inst.filter(getattr(self.model, self.field) == other)

    def __ne__(self, other):
        return self.inst.filter(getattr(self.model, self.field) != other)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
    
    def set_filter_params(self, query_params: list[tuple]) -> None:
        from src.core.utils import filter_query_param_values_extractor
        
        self.filter_params = filter_query_param_values_extractor(query_params)

    def perform_lookup(self, field, operation, value):
        self.field = field
        res = getattr(operator, operation)(self, value)
        return Lookup(self.model, res)
    
    def get_filtered_instances(self):
        for param in self.filter_params:
            self.inst = self.perform_lookup(*param).inst
        return self.inst