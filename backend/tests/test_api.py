import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app  # noqa: E402
from app.db.database import Base, engine  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test.db"):
        os.remove("test.db")


client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login():
    response = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "SecurePass123",
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

    # duplicate registration should fail
    response = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "SecurePass123",
    })
    assert response.status_code == 400

    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123",
    })
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials():
    response = client.post("/api/auth/login", json={
        "email": "nobody@example.com",
        "password": "wrongpass",
    })
    assert response.status_code == 401


def test_protected_route_requires_auth():
    response = client.get("/api/profile")
    assert response.status_code == 401


def test_job_description_and_analysis_flow():
    client.post("/api/auth/register", json={
        "full_name": "JD User",
        "email": "jduser@example.com",
        "password": "SecurePass123",
    })
    login = client.post("/api/auth/login", json={
        "email": "jduser@example.com",
        "password": "SecurePass123",
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    jd_response = client.post(
        "/api/job-descriptions",
        json={"title": "Backend Engineer", "raw_text": "We need a Python developer with FastAPI, PostgreSQL, and AWS experience. 3+ years experience required. Bachelor degree preferred."},
        headers=headers,
    )
    assert jd_response.status_code == 201
    assert jd_response.json()["title"] == "Backend Engineer"

    jd_list = client.get("/api/job-descriptions", headers=headers)
    assert jd_list.status_code == 200
    assert len(jd_list.json()) >= 1
