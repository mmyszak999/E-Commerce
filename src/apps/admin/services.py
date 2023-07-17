from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.apps.user.schemas import UserOutputSchema
from src.apps.user.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate


def modify_superuser_permission(session: Session, user_id: int, set_as_superuser: bool) -> dict[str, str]:
    if not (if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, user_id)
    
    update_data = {"is_superuser": set_as_superuser}
    statement = update(User).filter(User.id == user_id).values(**update_data)
    session.execute(statement)
    session.commit()
    
    return {"message": f"Superuser status has been {'granted' if set_as_superuser else 'revoked'} successfully"}


def grant_superuser_permission(session: Session, user_id: int) -> dict[str, str]:
    modify_superuser_permission(session, user_id, set_as_superuser=True)


def revoke_superuser_permission(session: Session, user_id: int) -> dict[str, str]:
    modify_superuser_permission(session, user_id, set_as_superuser=False)


def get_all_superusers(session: Session, page_params: PageParams) -> PagedResponseSchema:
    query = select(User).filter(User.is_superuser == True)

    return paginate(
        query=query,
        response_schema=UserOutputSchema,
        table=User,
        page_params=page_params,
        session=session,
    )
