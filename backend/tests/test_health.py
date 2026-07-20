"""Tests for the Phase 2 skeleton: health endpoint, request-id header, error shapes."""

from fastapi.testclient import TestClient


def test_health_check_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "InterviewOS"
    assert body["environment"] == "test"


def test_response_includes_request_id_header(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert "X-Request-ID" in response.headers


def test_request_id_is_echoed_back_when_provided(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "test-fixed-id"})

    assert response.headers["X-Request-ID"] == "test-fixed-id"


def test_security_headers_present(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_unknown_route_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    # FastAPI's default 404 for an unmatched route never reaches our
    # AppException handler (there's no route to raise it from), so this
    # checks the framework's built-in shape rather than our custom error
    # envelope — noting the distinction so it isn't mistaken for a bug.
    assert "detail" in response.json()


def test_openapi_schema_loads(client: TestClient) -> None:
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "InterviewOS"
