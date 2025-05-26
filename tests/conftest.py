import pytest
from app import create_app
from app.models import Base
from app.database import engine
from sqlalchemy.orm import sessionmaker

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": TEST_DB_URL,
        "JWT_SECRET_KEY": "test-secret"
    })

    with app.app_context():
        Base.metadata.drop_all(bind=engine)  # <-- reset DB
        Base.metadata.create_all(bind=engine)
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(client):
    """Register a test user."""
    client.post("/api/register", json={
        "user_name": "testuser",
        "password": "1234"
    })

@pytest.fixture
def auth_token(client, test_user):
    """Login and return a valid token"""
    res = client.post("/api/auth/login", json={
        "user_name": "testuser",
        "password": "1234"
    })
    return res.get_json()["access_token"]

@pytest.fixture
def sample_notes(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    notes = [
        {"title": "DevOps", "content": "About pipelines", "tags": "devops,ci"},
        {"title": "Flask Tips", "content": "Use blueprints", "tags": "flask,backend"},
        {"title": "React Guide", "content": "Hooks are powerful", "tags": "react,frontend"},
    ]
    for note in notes:
        client.post("/api/notes", json=note, headers=headers)
