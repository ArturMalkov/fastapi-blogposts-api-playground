from app import schemas
from tests.database import client, db_session


# def test_root(client):
#     response = client.get("/")
#     print(response.json().get("message"))
#     assert response.json().get("message") == "Hello World"
#     assert response.status_code == 200


def test_create_user(client):
    response = client.post("/users", json={"email": "hello123@example.com", "password": "password123"})
    assert response.status_code == 201
    new_user = schemas.UserOut(**response.json())
    # assert response.json().get("email") == "hello123@example.com"
    assert new_user.email == "hello123@example.com"


def test_login_user(client):
    response = client.post("/login", data={"username": "hello123@example.com", "password": "password123"})
    assert response.status_code == 200
