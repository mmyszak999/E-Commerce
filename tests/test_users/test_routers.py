from tests.test_users.fixtures import client


def test_create_user(client=client):
    response = client.post("api/users/register", json={
        "first_name": "string_aaa",
        "last_name": "string_aaa",
        "email": "string_aaaa",
        "birth_date": "2022-09-04",
        "username": "string_aaa",
        "password": "stringst",
        "password_repeat": "stringst"}
    )
    response2 = client.get("api/users")
    print(response2.json())
    assert response.status_code == 201
