from fastapi import HTTPException

user_does_not_exist_exception = HTTPException(status_code=404, detail="User does not exist")