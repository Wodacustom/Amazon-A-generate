"""Redis 客户端单例管理。"""

from redis.asyncio import Redis

from app.core.config import settings

_redis: Redis | None = None


def get_redis() -> Redis:
    """懒加载 Redis 连接。"""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    """关闭 Redis 连接，用于 FastAPI 生命周期退出。"""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
