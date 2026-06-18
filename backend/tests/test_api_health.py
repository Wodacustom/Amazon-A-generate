from fastapi.testclient import TestClient

from app.main import create_app


def test_health_contract_has_dependency_checks():
    response = TestClient(create_app()).get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "aplus-agent-api"
    assert {"postgres", "pgvector", "redis", "rustfs"}.issubset(body["checks"])
