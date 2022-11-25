import pytest

from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.config import settings
from app.database import get_db
from app.main import app
from app.oauth2 import create_access_token


# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Kleopatra2003!@localhost:5433/blogposts_test"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}" \
                          f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture
def db_session():
    # drop and create tables before we run our test - using SQLAlchemy
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    # drop and create tables before we run our test - using Alembic
    # command.upgrade("head")  # create tables before we run our test - using Alembic
    # command.downgrade("base")  # drop tables after we run our test - using Alembic

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# client uses testing database as a result of dependency override above
@pytest.fixture
def client(db_session):
    # Testing database dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # substitute 'get_db' dependency (returning dev database session) with dependency returning testing database session
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@example.com", "password": "password123"}
    response = client.post("/users", json=user_data)
    assert response.status_code == 201

    new_user = response.json()
    new_user["password"] = user_data["password"]  # since password is not included in UserOut response model
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "2hello123@example.com", "password": "password123"}
    response = client.post("/users", json=user_data)
    assert response.status_code == 201

    new_user = response.json()
    new_user["password"] = user_data["password"]  # since password is not included in UserOut response model
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):  # to deal with path operations requiring authentication
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, test_user2, db_session):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "user_id": test_user["id"]
    }, {
        "title": "second title",
        "content": "second content",
        "user_id": test_user["id"]
    }, {
        "title": "third title",
        "content": "third content",
        "user_id": test_user["id"]
    }, {
        "title": "fourth title",
        "content": "fourth content",
        "user_id": test_user2["id"]
    }]

    db_session.add_all([models.Post(**post) for post in posts_data])
    db_session.commit()

    posts = db_session.query(models.Post).all()

    return posts
