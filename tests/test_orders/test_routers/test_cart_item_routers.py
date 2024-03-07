from fastapi import status
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT

from src.apps.orders.schemas import (
    CartOutputSchema,
    CartItemOutputSchema
)
from src.apps.products.schemas import ProductOutputSchema
from src.apps.user.schemas import UserOutputSchema
from src.core.factories import CartItemInputSchemaFactory, CartItemUpdateSchemaFactory
from tests.test_products.conftest import db_products
from tests.test_orders.conftest import db_carts, db_cart_items
from tests.test_users.conftest import db_user, db_staff_user, staff_auth_headers, auth_headers


def test_authenticated_user_can_add_item_to_their_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    new_cart_item = CartItemInputSchemaFactory().generate(product_id=db_products[2].id)
    
    response = sync_client.post(f"carts/{cart.id}/items/", headers=auth_headers, data=new_cart_item.json())
 
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["cart_id"] == cart.id

def test_staff_user_can_add_item_to_any_cart(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    new_cart_item = CartItemInputSchemaFactory().generate(product_id=db_products[1].id)
    
    response = sync_client.post(f"carts/{cart.id}/items/", headers=staff_auth_headers, data=new_cart_item.json())
 
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["cart_id"] == cart.id

def test_anonymous_user_cannot_add_item_to_the_cart(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    new_cart_item = CartItemInputSchemaFactory().generate(product_id=db_products[1].id)
    
    response = sync_client.post(f"carts/{cart.id}/items/", data=new_cart_item.json())
 
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_user_can_re_add_item_to_their_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    """
    re-adding item in this context means making POST request to add item to the current cart
    when such an item is already in the cart. The request then, can only change the cart item quantity
    if provided
    """
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    new_cart_item = CartItemInputSchemaFactory().generate(quantity=21, product_id=db_products[2].id)
    
    response = sync_client.post(f"carts/{cart.id}/items/", headers=auth_headers, data=new_cart_item.json())
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["quantity"] == new_cart_item.quantity

def test_staff_user_can_re_add_item_to_any_cart(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    new_cart_item = CartItemInputSchemaFactory().generate(quantity=21, product_id=db_products[2].id)
    
    response = sync_client.post(f"carts/{cart.id}/items/", headers=staff_auth_headers, data=new_cart_item.json())
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["quantity"] == new_cart_item.quantity
    
def test_authenticated_user_cannot_add_item_to_not_their_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema]
):
    cart_id = db_carts.results[0].id
    new_cart_item = CartItemInputSchemaFactory().generate(product_id=db_products[0].id)
    response = sync_client.post(f"carts/{cart_id}/items/", headers=auth_headers, data=new_cart_item.json())
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_authenticated_user_can_get_single_cart_item(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.get(f"carts/{cart.id}/items/{cart.cart_items[0].id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == cart.cart_items[0].id

def test_authenticated_user_cannot_get_single_cart_item_from_not_their_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_staff_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_staff_user.id][0]
    
    response = sync_client.get(f"carts/{cart.id}/items/{cart.cart_items[0].id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_anonymous_user_cannot_get_single_cart_item(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.get(f"carts/{cart.id}/items/{cart.cart_items[0].id}")
 
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_staff_user_can_get_cart_items_for_any_cart(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.get(f"carts/{cart.id}/items/", headers=staff_auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(cart.cart_items)


def test_staff_user_can_get_cart_items_for_any_cart(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.get(f"carts/{cart.id}/items/", headers=staff_auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(cart.cart_items)


def test_authenticated_user_can_get_cart_items_for_their_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.get(f"carts/{cart.id}/items/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == len(cart.cart_items)

def test_authenticated_user_cannot_get_cart_items_for_not_their_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_staff_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_staff_user.id][0]
    
    response = sync_client.get(f"carts/{cart.id}/items/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_anonymous_user_cannot_get_cart_items(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.get(f"carts/{cart.id}/items/")
 
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_user_can_update_their_cart_item(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    update_data = CartItemUpdateSchemaFactory().generate(quantity=21)
    
    response = sync_client.patch(
        f"carts/{cart.id}/items/{cart.cart_items[0].id}",headers=auth_headers, data=update_data.json()
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["quantity"] == update_data.quantity


def test_staff_user_can_update_any_cart_item(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    update_data = CartItemUpdateSchemaFactory().generate(quantity=21)
    
    response = sync_client.patch(
        f"carts/{cart.id}/items/{cart.cart_items[0].id}",headers=staff_auth_headers, data=update_data.json()
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["quantity"] == update_data.quantity

def test_authenticated_user_cannot_update_cart_item_from_not_their_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_staff_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_staff_user.id][0]
    update_data = CartItemUpdateSchemaFactory().generate(quantity=21)
    
    response = sync_client.patch(
        f"carts/{cart.id}/items/{cart.cart_items[0].id}", headers=auth_headers, data=update_data.json()
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_anonnymous_user_cannot_update_cart_item(
    sync_client: TestClient, db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_staff_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_staff_user.id][0]
    update_data = CartItemUpdateSchemaFactory().generate(quantity=21)
    
    response = sync_client.patch(
        f"carts/{cart.id}/items/{cart.cart_items[0].id}", data=update_data.json()
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_user_can_delete_cart_item(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.delete(
        f"carts/{cart.id}/items/{cart.cart_items[0].id}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_staff_user_can_delete_any_cart_item(
    sync_client: TestClient, staff_auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.delete(
        f"carts/{cart.id}/items/{cart.cart_items[0].id}", headers=staff_auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_authenticated_user_cannot_delete_cart_item_from_not_their_cart(
    sync_client: TestClient, auth_headers: dict[str, str],
    db_cart_items: list[CartItemOutputSchema], db_carts: list[CartOutputSchema],
    db_products: list[ProductOutputSchema], db_staff_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_staff_user.id][0]
    
    response = sync_client.delete(
        f"carts/{cart.id}/items/{cart.cart_items[0].id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_anonymous_user_cannot_delete_cart_item(
    sync_client: TestClient, db_cart_items: list[CartItemOutputSchema],
    db_carts: list[CartOutputSchema], db_products: list[ProductOutputSchema],
    db_user: UserOutputSchema
):
    cart = [cart for cart in db_carts.results if cart.user_id == db_user.id][0]
    
    response = sync_client.delete(f"carts/{cart.id}/items/{cart.cart_items[0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED




