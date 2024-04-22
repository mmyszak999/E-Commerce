from typing import Any


class ServiceException(Exception):
    pass


class DoesNotExist(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{class_name} with {field}={value} does not exist")


class AlreadyExists(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{class_name} with {field}={value} already exists")


class IsOccupied(ServiceException):
    def __init__(self, class_name: str, field: str, value: Any) -> None:
        super().__init__(f"{field}={value} value of {class_name} is occupied")


class AuthenticationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class AuthorizationException(ServiceException):
    def __init__(self, message: str) -> None:
        super().__init__(f"{message}")


class AccountNotActivatedException(ServiceException):
    def __init__(self, field: str, value: Any) -> None:
        super().__init__(
            f"The account of the user with {field}={value} has not been activated! "
            "Please check your mailbox to find the message with activation link! "
        )


class NegativeQuantityException(ServiceException):
    def __init__(self, value: Any) -> None:
        super().__init__(
            f"The quantity of the product can't be negative (You entered quantity = {value})! "
        )


class ActiveCartException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            "Can't create another cart when other one is active! "
            "Please empty the active cart before creating a new cart! "
        )


class ExceededItemQuantityException(ServiceException):
    def __init__(self, product_quantity: int, entered_quantity: int) -> None:
        super().__init__(
            f"Requested quantity of the product({entered_quantity}) is bigger than the available one ({product_quantity})! "
            "Please change the quantity you entered!"
        )


class NonPositiveCartItemQuantityException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            "Requested quantity of the product is equal to 0! Please change the item quantity to a positive integer!"
        )


class EmptyCartException(ServiceException):
    def __init__(self) -> None:
        super().__init__("You have no items in the cart!")


class NoSuchItemInCartException(ServiceException):
    def __init__(self) -> None:
        super().__init__("No such item in the cart!")


class CartItemWithZeroQuantityException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            "The requested product quantity of cart item is equal to 0, so the item will be removed from the cart!"
        )


class QuantityLowerThanAmountOfProductItemsInCartsException(ServiceException):
    def __init__(self) -> None:
        super().__init__(
            "The requested quantity is lower than the amount of the product item in the active carts! Please change the value!"
        )


class OrderAlreadyCancelledException(ServiceException):
    def __init__(self) -> None:
        super().__init__("Order is already cancelled!")
        

class ProductAlreadyRemovedFromStoreException(ServiceException):
    def __init__(self) -> None:
        super().__init__("Product is already removed from store")


class ProductRemovedFromStoreException(ServiceException):
    def __init__(self) -> None:
        super().__init__("Product removed from store and no action can be proceed with this product!")
