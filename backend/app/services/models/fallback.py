"""模型熔断/降级执行。"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from app.core.logging import get_logger

T = TypeVar("T")
logger = get_logger(__name__)


@dataclass(frozen=True)
class FallbackResult[T]:
    """降级执行结果。"""

    value: T
    fallback_used: bool
    failure_reason: str | None = None


class FallbackExecutor:
    """主模型失败后切备用模型。

    第一版只做单次请求级降级；后续可在这里增加失败计数、熔断窗口和恢复探测。
    """

    async def run(
        self,
        primary: Callable[[], Awaitable[T]],
        fallback: Callable[[], Awaitable[T]] | None = None,
    ) -> FallbackResult[T]:
        """执行主调用；主调用抛异常且存在备用调用时自动降级。"""
        try:
            return FallbackResult(value=await primary(), fallback_used=False)
        except Exception as exc:
            if fallback is None:
                raise
            logger.warning(
                "model.fallback.triggered",
                extra={"event": "model.fallback.triggered", "failure_reason": str(exc)},
            )
            return FallbackResult(value=await fallback(), fallback_used=True, failure_reason=str(exc))
