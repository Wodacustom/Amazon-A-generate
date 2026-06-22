"""健康检查接口测试。"""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_contract_has_dependency_checks():
    """验证 health 响应包含所有外部依赖检查项。"""
    response = TestClient(create_app()).get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "aplus-agent-api"
    assert {"postgres", "pgvector", "redis", "rustfs"}.issubset(body["checks"])


def test_request_id_header_is_returned():
    """验证请求日志中间件会透传 request id。"""
    response = TestClient(create_app()).get("/api/health", headers={"X-Request-ID": "test-request-id"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-id"
