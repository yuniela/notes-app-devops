import pytest
from app import create_app
from app.database import Base, engine, SessionLocal
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        Base.metadata.create_all(bind=engine)

    yield app

@pytest.fixture
def client(app):
    return app.test_client()
