from passlib.context import CryptContext

from src.apps.user.schemas.schemas import UserRegisterSchema

def hash_user_password(user_schema: UserRegisterSchema) -> None:
    passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user_data = user_schema.dict()
    password_repeat = user_data.pop("password_repeat")
    user_data['password'] = passwd_context.hash(password_repeat)