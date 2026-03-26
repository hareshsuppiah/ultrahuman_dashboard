"""Tests for the Flask application: app setup, user routes, and metrics routes."""

import json
import os
import tempfile

import pytest

from src.main import app
from src.models.user import db, User


@pytest.fixture
def client():
    """Create a test client with an in-memory SQLite database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


@pytest.fixture
def sample_user(client):
    """Create a sample user and return the response data."""
    response = client.post(
        "/api/users",
        data=json.dumps({
            "email": "test@example.com",
            "api_key": "test-api-key-123",
            "access_code": "test-access-code",
        }),
        content_type="application/json",
    )
    return json.loads(response.data)


# ---------------------------------------------------------------------------
# App configuration tests
# ---------------------------------------------------------------------------

class TestAppConfig:
    def test_app_exists(self):
        assert app is not None

    def test_app_has_secret_key(self):
        assert app.config["SECRET_KEY"] is not None

    def test_blueprints_registered(self):
        blueprint_names = list(app.blueprints.keys())
        assert "user" in blueprint_names
        assert "metrics" in blueprint_names

    def test_static_folder_configured(self):
        assert app.static_folder is not None

    def test_index_page_served(self, client):
        response = client.get("/")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# User CRUD tests
# ---------------------------------------------------------------------------

class TestCreateUser:
    def test_create_user_success(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({
                "email": "new@example.com",
                "api_key": "key-123",
                "access_code": "code-456",
            }),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["email"] == "new@example.com"
        assert data["api_key"] == "key-123"
        assert "id" in data

    def test_create_user_missing_email(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"api_key": "key", "access_code": "code"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_user_missing_api_key(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"email": "a@b.com", "access_code": "code"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_user_missing_access_code(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({"email": "a@b.com", "api_key": "key"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_user_empty_body(self, client):
        response = client.post(
            "/api/users",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_create_duplicate_email(self, client, sample_user):
        response = client.post(
            "/api/users",
            data=json.dumps({
                "email": "test@example.com",
                "api_key": "different-key",
                "access_code": "different-code",
            }),
            content_type="application/json",
        )
        assert response.status_code == 409


class TestGetUsers:
    def test_get_users_empty(self, client):
        response = client.get("/api/users")
        assert response.status_code == 200
        assert json.loads(response.data) == []

    def test_get_users_with_data(self, client, sample_user):
        response = client.get("/api/users")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["email"] == "test@example.com"

    def test_get_single_user(self, client, sample_user):
        user_id = sample_user["id"]
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["email"] == "test@example.com"

    def test_get_nonexistent_user(self, client):
        response = client.get("/api/users/999")
        assert response.status_code == 404


class TestUpdateUser:
    def test_update_user_email(self, client, sample_user):
        user_id = sample_user["id"]
        response = client.put(
            f"/api/users/{user_id}",
            data=json.dumps({"email": "updated@example.com"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["email"] == "updated@example.com"

    def test_update_nonexistent_user(self, client):
        response = client.put(
            "/api/users/999",
            data=json.dumps({"email": "x@y.com"}),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_update_user_no_data(self, client, sample_user):
        user_id = sample_user["id"]
        response = client.put(
            f"/api/users/{user_id}",
            data=json.dumps(None),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_update_duplicate_email(self, client, sample_user):
        # Create a second user
        client.post(
            "/api/users",
            data=json.dumps({
                "email": "other@example.com",
                "api_key": "key2",
                "access_code": "code2",
            }),
            content_type="application/json",
        )
        # Try to update first user's email to second user's email
        user_id = sample_user["id"]
        response = client.put(
            f"/api/users/{user_id}",
            data=json.dumps({"email": "other@example.com"}),
            content_type="application/json",
        )
        assert response.status_code == 409


class TestDeleteUser:
    def test_delete_user(self, client, sample_user):
        user_id = sample_user["id"]
        response = client.delete(f"/api/users/{user_id}")
        assert response.status_code == 200
        # Verify user is gone
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client):
        response = client.delete("/api/users/999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Metrics route tests
# ---------------------------------------------------------------------------

class TestMetricsRoute:
    def test_metrics_missing_date(self, client, sample_user):
        user_id = sample_user["id"]
        response = client.get(f"/api/metrics/{user_id}")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Date parameter" in data["error"]

    def test_metrics_invalid_date_format(self, client, sample_user):
        user_id = sample_user["id"]
        response = client.get(f"/api/metrics/{user_id}?date=13-01-2025")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid date format" in data["error"]

    def test_metrics_nonexistent_user(self, client):
        response = client.get("/api/metrics/999?date=2025-01-01")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# User model tests
# ---------------------------------------------------------------------------

class TestUserModel:
    def test_user_repr(self, client):
        with app.app_context():
            user = User(email="repr@test.com", api_key="k", access_code="c")
            assert "repr@test.com" in repr(user)

    def test_user_serialize_without_credentials(self, client):
        with app.app_context():
            user = User(email="ser@test.com", api_key="mykey", access_code="mycode")
            db.session.add(user)
            db.session.commit()
            data = user.serialize()
            assert data["email"] == "ser@test.com"
            assert "api_key" not in data
            assert "access_code" not in data
            assert "id" in data

    def test_user_serialize_with_credentials(self, client):
        with app.app_context():
            user = User(email="ser2@test.com", api_key="mykey", access_code="mycode")
            db.session.add(user)
            db.session.commit()
            data = user.serialize(include_credentials=True)
            assert data["email"] == "ser2@test.com"
            assert data["api_key"] == "mykey"
            assert data["access_code"] == "mycode"
            assert "id" in data
