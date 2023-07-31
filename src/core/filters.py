import operator

from sqlalchemy.sql.expression import Select


class Lookup(Select):
    def __init__(self, model, inst):
        self.model = model
        self.inst = inst
        self.field = None

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

    def perform_lookup(self, field, operation, value):
        self.field = field
        res = getattr(operator, operation)(self, value)
        return Lookup(self.model, res)
