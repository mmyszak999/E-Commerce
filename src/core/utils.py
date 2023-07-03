import json
from typing import Any
from datetime import date, datetime

from sqlalchemy import Table, select
from sqlalchemy.orm import Session

def if_exists(model_class: Table, field: str, value: Any, session: Session) -> bool:
    return session.scalar(select(model_class).filter(getattr(model_class, field) == value))


class DateJSONEncoder(json.JSONEncoder):
    def default(self, obj) -> str:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f'Type {type(obj)} is not serializable')
        

