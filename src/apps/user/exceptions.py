from fastapi import HTTPException, status


user_does_not_exist_exception=HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist.", 
    )

user_already_exists_exception=HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists."
    )

username_is_occupied_exception=HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Username is occupied."
    )

email_is_occupied_exception=HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Email is occupied."
    )

auth_exception=HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
    )