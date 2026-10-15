from collections.abc import Generator
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app import models  # noqa: F401


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_health_and_service_info(client: TestClient):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/").json()["service"] == "taskboard-api"


def test_readiness_checks_database(client: TestClient):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


def test_task_crud_and_stats(client: TestClient):
    payload = {
        "title": "Prepare capstone demo",
        "description": "Verify all stages",
        "status": "In Progress",
        "priority": "High",
        "assignee": "Harish",
        "due_date": str(date.today() + timedelta(days=1)),
    }
    created_response = client.post("/api/tasks", json=payload)
    assert created_response.status_code == 201
    created = created_response.json()
    task_id = created["id"]
    assert created["title"] == payload["title"]

    listed = client.get("/api/tasks").json()
    assert any(task["id"] == task_id for task in listed)
    assert client.get(f"/api/tasks/{task_id}").json()["id"] == task_id

    updated_response = client.put(f"/api/tasks/{task_id}", json={"status": "Done"})
    assert updated_response.status_code == 200
    assert updated_response.json()["status"] == "Done"

    stats = client.get("/api/tasks/stats").json()
    assert stats["total"] == 1
    assert stats["completed"] == 1
    assert stats["in_progress"] == 0

    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_search_and_status_filter(client: TestClient):
    client.post("/api/tasks", json={"title": "Design landing page", "priority": "Medium"})
    client.post("/api/tasks", json={"title": "Ship API", "status": "In Progress", "priority": "High"})
    assert len(client.get("/api/tasks", params={"status": "In Progress"}).json()) == 1
    assert len(client.get("/api/tasks", params={"q": "landing"}).json()) == 1


def test_validation_rejects_blank_title(client: TestClient):
    response = client.post("/api/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_not_found_for_unknown_task(client: TestClient):
    assert client.get("/api/tasks/987654").status_code == 404


def test_metrics_endpoint(client: TestClient):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "taskboard_http_requests_total" in response.text
