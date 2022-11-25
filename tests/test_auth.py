import pytest
from jose import jwt

from app import schemas
from app.config import settings


def test_login_user(test_user, client):
    response = client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})
    assert response.status_code == 200

    # check whether token contains user_id
    login_response = schemas.Token(**response.json())
    assert login_response.token_type == "bearer"
    payload = jwt.decode(login_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user["id"]


@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "password123", 403),
    ("hello123@example.com", "wrongpassword", 403),
    ("wrongemail@gmail.com", "wrongpassword", 403),
    (None, "password123", 422),
    ("hello123@example.com", None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    response = client.post("/login", data={"username": email, "password": password})
    assert response.status_code == status_code
    # assert response.json().get("detail") == "Invalid credentials."  # it won't apply to 422 status code
