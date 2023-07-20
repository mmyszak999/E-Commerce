from fastapi_jwt_auth import AuthJWT
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.user.models import User
from src.apps.user.schemas import (UserLoginInputSchema, UserOutputSchema,
                                   UserRegisterSchema, UserUpdateSchema)
from src.apps.user.utils import passwd_context
from src.core.exceptions import (AlreadyExists, AuthenticationException,
                                 DoesNotExist, IsOccupied)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils import if_exists


def hash_user_password(password: str) -> str:
    return passwd_context.hash(password)


def register_user(session: Session, user: UserRegisterSchema) -> UserOutputSchema:
    user_data = user.dict()
    if user_data.pop("password_repeat"):
        user_data["password"] = hash_user_password(password=user_data.pop("password"))

    username_check = session.scalar(
        select(User).filter(User.username == user_data["username"]).limit(1)
    )
    email_check = session.scalar(
        select(User).filter(User.email == user_data["email"]).limit(1)
    )

    if username_check:
        raise AlreadyExists(User.__name__, "username", user.username)
    if email_check:
        raise AlreadyExists(User.__name__, "email", user.email)

    new_user = User(**user_data)

    session.add(new_user)
    session.commit()

    return UserOutputSchema.from_orm(new_user)


def authenticate(username: str, password: str, session: Session) -> User:
    user = session.scalar(select(User).filter(User.username == username).limit(1))
    if not (user or passwd_context.verify(password, user.password)):
        raise AuthenticationException("Invalid Credentials")
    return user


def get_access_token_schema(
    user_login_schema: UserLoginInputSchema, session: Session, auth_jwt: AuthJWT
) -> str:
    user = authenticate(**user_login_schema.dict(), session=session)
    username = user.username
    access_token = auth_jwt.create_access_token(subject=username, algorithm="HS256")

    return AccessTokenOutputSchema(access_token=access_token)


def get_single_user(session: Session, user_id: int) -> UserOutputSchema:
    if not (user_object := if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, user_id)

    return UserOutputSchema.from_orm(user_object)


def get_all_users(session: Session, page_params: PageParams) -> PagedResponseSchema:
    query = select(User)

    return paginate(
        query=query,
        response_schema=UserOutputSchema,
        table=User,
        page_params=page_params,
        session=session,
    )


def update_single_user(
    session: Session, user: UserUpdateSchema, user_id: int
) -> UserOutputSchema:
    if not if_exists(User, "id", user_id, session):
        raise DoesNotExist(User.__name__, user_id)

    user_data = user.dict(exclude_unset=True)
    if user_data.get("username"):
        username_check = session.scalar(
            select(User).filter(User.username == user.username).limit(1)
        )

        if username_check:
            raise IsOccupied(User.__name__, "username", user.username)

    statement = update(User).filter(User.id == user_id).values(**user_data)

    session.execute(statement)
    session.commit()

    return get_single_user(session, user_id=user_id)


def delete_single_user(session: Session, user_id: int):
    if not if_exists(User, "id", user_id, session):
        raise DoesNotExist(User.__name__, user_id)

    statement = delete(User).filter(User.id == user_id)
    result = session.execute(statement)
    session.commit()

    return result
