from fastapi import HTTPException, status

category_does_not_exist_exception=HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Category doesn't exist.", 
    )

category_already_exists_exception=HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists."
    )

category_name_is_occupied_exception=HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Category name is occupied."
    )

product_does_not_exist_exception=HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Product doesn't exist.", 
    )

product_already_exists_exception=HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Product already exists."
    )

product_name_is_occupied_exception=HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Product name is occupied."
    )