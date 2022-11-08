from passlib.context import CryptContext

def hash_user_password(password: str) -> str:
    passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return passwd_context.hash(password)