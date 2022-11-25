import pytest

from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.config import settings
from app.database import get_db
from app.main import app


# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Kleopatra2003!@localhost:5433/blogposts_test"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}" \
                          f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="module")
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
@pytest.fixture(scope="module")
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
