"""结构化业务日志工具。"""

import contextvars
import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

_RESERVED_LOG_RECORD_KEYS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}

_SENSITIVE_KEYS = {"api_key", "authorization", "password", "token", "encrypted_api_key", "secret"}


class JsonFormatter(logging.Formatter):
    """把日志记录格式化为单行 JSON。"""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None) or request_id_var.get()
        if request_id:
            payload["request_id"] = request_id
        for key, value in record.__dict__.items():
            if key in _RESERVED_LOG_RECORD_KEYS or key.startswith("_"):
                continue
            payload[key] = sanitize_log_value(key, value)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> None:
    """配置应用日志为 stdout JSON 输出。"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.log_level.upper())
    logging.getLogger("uvicorn.access").disabled = True


def get_logger(name: str) -> logging.Logger:
    """获取业务 logger。"""
    return logging.getLogger(name)


def sanitize_log_value(key: str, value: Any) -> Any:
    """清洗日志字段，避免敏感信息或大对象进入日志。"""
    lowered = key.lower()
    if any(sensitive in lowered for sensitive in _SENSITIVE_KEYS):
        return "***"
    if isinstance(value, dict):
        return {k: sanitize_log_value(str(k), v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_log_value(key, item) for item in value[:20]]
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    if isinstance(value, str) and len(value) > 500:
        return f"{value[:500]}...<truncated:{len(value)}>"
    return value


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """为每个请求生成 request_id，并记录开始、结束和异常。"""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        token = request_id_var.set(request_id)
        logger = get_logger("app.request")
        started = time.perf_counter()
        logger.info(
            "request.start",
            extra={
                "event": "request.start",
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None,
            },
        )
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request.error",
                extra={
                    "event": "request.error",
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            request_id_var.reset(token)
            raise
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request.finish",
            extra={
                "event": "request.finish",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        request_id_var.reset(token)
        return response
