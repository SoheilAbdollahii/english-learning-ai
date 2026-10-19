import pytest
from django.db import OperationalError
from django.test import Client


@pytest.mark.django_db
def test_readiness_checks_database_and_migrations():
    response = Client().get("/api/v1/ready/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"database": "ok", "migrations": "applied"},
    }


@pytest.mark.django_db
def test_readiness_fails_closed_without_database(monkeypatch):
    from apps.accounts import health_views

    def fail_connection():
        raise OperationalError("private connection detail")

    monkeypatch.setattr(health_views.connection, "ensure_connection", fail_connection)
    response = Client().get("/api/v1/ready/")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert "private connection detail" not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_readiness_reports_pending_migrations_without_leaking_details(monkeypatch):
    from apps.accounts import health_views

    class FakeGraph:
        def leaf_nodes(self):
            return [("accounts", "9999_test")]

    class FakeLoader:
        graph = FakeGraph()

    class FakeExecutor:
        def __init__(self, _connection):
            self.loader = FakeLoader()

        def migration_plan(self, _leaf_nodes):
            return [object()]

    monkeypatch.setattr(health_views, "MigrationExecutor", FakeExecutor)
    response = Client().get("/api/v1/ready/")
    assert response.status_code == 503
    assert response.json()["checks"]["migrations"] == "pending"
