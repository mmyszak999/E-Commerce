from typing import Any

from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.apps.emails.services import send_activation_email
from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.apps.user.models import User, UserAddress
from src.apps.user.schemas import (
    UserLoginInputSchema,
    UserOutputSchema,
    UserRegisterSchema,
    UserUpdateSchema,
)
from src.apps.user.utils import passwd_context
from src.core.exceptions import (
    AccountNotActivatedException,
    AlreadyExists,
    AuthenticationException,
    DoesNotExist,
    IsOccupied,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.utils import confirm_token, filter_and_sort_instances, if_exists


def hash_user_password(password: str) -> str:
    return passwd_context.hash(password)


def register_user_base(session: Session, user: UserRegisterSchema) -> tuple[Any]:
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

    if user_data.get("address"):
        address_data = user_data.pop("address")

    new_user = User(**user_data)
    new_address = UserAddress(**address_data)

    return new_user, new_address


def register_user(
    session: Session, user: UserRegisterSchema, background_tasks: BackgroundTasks
) -> UserOutputSchema:
    new_user, new_address = register_user_base(session, user)

    session.add(new_user)
    session.commit()

    new_address.user_id = new_user.id
    session.add(new_address)
    session.commit()

    send_activation_email(new_user.email, session, background_tasks)

    return UserOutputSchema.from_orm(new_user)


def activate_account(session: Session, email: str) -> None:
    user = if_exists(User, "email", email, session)

    if user is None:
        raise DoesNotExist(User.__name__, "email", email)

    if user.is_active:
        raise ServiceException("This account was already activated!")

    statement = update(User).filter(User.email == email).values(is_active=True)
    session.execute(statement)
    session.commit()


def activate_account_service(session: Session, token: str) -> None:
    emails = confirm_token(token)
    current_email = emails[0]
    activate_account(session, current_email)


def authenticate(user_login_schema: UserLoginInputSchema, session: Session) -> User:
    login_data = user_login_schema.dict()
    user = session.scalar(
        select(User).filter(User.email == login_data["email"]).limit(1)
    )
    if not (user or passwd_context.verify(login_data["password"], user.password)):
        raise AuthenticationException("Invalid Credentials")
    if not user.is_active:
        raise AccountNotActivatedException("email", login_data["email"])
    return user


def get_access_token_schema(
    user_login_schema: UserLoginInputSchema, session: Session, auth_jwt: AuthJWT
) -> str:
    user = authenticate(user_login_schema, session=session)
    email = user.email
    access_token = auth_jwt.create_access_token(subject=email, algorithm="HS256")

    return AccessTokenOutputSchema(access_token=access_token)


def get_single_user(
    session: Session, user_id: str, output_schema: BaseModel = UserOutputSchema
) -> BaseModel:
    if not (user_object := if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)

    return output_schema.from_orm(user_object)


def get_all_users(
    session: Session, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema:
    query = select(User)
    if query_params:
        query = filter_and_sort_instances(query_params, query, User)

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
        raise DoesNotExist(User.__name__, "id", user_id)

    user_data = user.dict(exclude_unset=True, exclude_none=True)
    if user_data.get("username"):
        username_check = session.scalar(
            select(User).filter(User.username == user.username).limit(1)
        )

        if username_check:
            raise IsOccupied(User.__name__, "username", user.username)

    if "address" in user_data.keys():
        if user_data.get("address"):
            address_data = user_data.pop("address")
            print(user_data)
            statement = (
                update(UserAddress)
                .filter(UserAddress.user_id == user_id)
                .values(**address_data)
            )

            session.execute(statement)
            session.commit()

        else:
            user_data.pop("address")

    if user_data:
        statement = update(User).filter(User.id == user_id).values(**user_data)

        session.execute(statement)
        session.commit()

    return get_single_user(session, user_id=user_id)


def delete_single_user(session: Session, user_id: int):
    if not if_exists(User, "id", user_id, session):
        raise DoesNotExist(User.__name__, "id", user_id)

    statement = delete(User).filter(User.id == user_id)
    result = session.execute(statement)
    session.commit()

    return result
