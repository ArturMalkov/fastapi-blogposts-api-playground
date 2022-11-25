from app import schemas


def test_create_user(client):
    response = client.post("/users", json={"email": "hello123@example.com", "password": "password123"})
    assert response.status_code == 201

    new_user = schemas.UserOut(**response.json())
    # assert response.json().get("email") == "hello123@example.com"
    assert new_user.email == "hello123@example.com"

