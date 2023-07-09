from datetime import date, datetime
from typing import Any

from sqlalchemy import Table, select
from sqlalchemy.orm import Session


def if_exists(model_class: Table, field: str, value: Any, session: Session) -> bool:
    return session.scalar(
        select(model_class).filter(getattr(model_class, field) == value)
    )
