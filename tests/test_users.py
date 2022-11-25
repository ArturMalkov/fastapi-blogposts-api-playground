import pytest

from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models, schemas
from app.config import settings
from app.database import get_db
from app.main import app


# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Kleopatra2003!@localhost:5433/blogposts_test"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}" \
                          f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Testing database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# substitute 'get_db' dependency (returning dev database session) with dependency returning testing database session
app.dependency_overrides[get_db] = override_get_db


# client uses testing database as a result of dependency override above
@pytest.fixture
def client():
    # drop and create tables before we run our test
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield TestClient(app)


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


def test_get_user():
    pass
