from tests.test_users.fixtures import client


def test_create_user(client=client):
    response = client.post("api/users/register", json={
        "first_name": "bbdw",
        "last_name": "ccdw",
        "email": "xxdw",
        "birth_date": "2021-02-03",
        "username": "bcxbcxdw",
        "password": "stringst",
        "password_repeat": "stringst"}
    )
    assert response.status_code == 201
