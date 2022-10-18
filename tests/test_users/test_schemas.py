from fastapi import status
from fastapi.testclient import TestClient

def test_passwords_are_not_identical(
    sync_client: TestClient,
    incorrect_passwords_dict: dict[str, str]
):
    response = sync_client.post('users/register', json=incorrect_passwords_dict)
    error_message = response.json()["detail"][0]["msg"]
    error_type = response.json()["detail"][0]["type"]

    assert error_message == 'Passwords are not identical'
    assert error_type == "value_error"
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_date_is_from_future(
    sync_client: TestClient,
    date_from_future_dict: dict[str, str]
):
    response = sync_client.post('users/register', json=date_from_future_dict)
    error_message = response.json()["detail"][0]["msg"]
    error_type = response.json()["detail"][0]["type"]

    assert error_message == 'Birth date must be in the past'
    assert error_type == "value_error"

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY






    



