import asyncio

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_sessionmaker
from app.services.redis_client import get_redis
from app.services.storage import get_storage

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    checks = {"postgres": False, "pgvector": False, "redis": False, "rustfs": False}
    try:
        await asyncio.wait_for(_check_postgres(checks), timeout=1)
    except Exception:
        pass

    try:
        checks["redis"] = bool(await asyncio.wait_for(get_redis().ping(), timeout=1))
    except Exception:
        pass

    try:
        await asyncio.wait_for(get_storage().ensure_bucket(), timeout=1)
        checks["rustfs"] = True
    except Exception:
        pass

    status = "ok" if all(checks.values()) else "degraded"
    return {"status": status, "service": settings.app_name, "version": settings.app_version, "checks": checks}


async def _check_postgres(checks: dict[str, bool]) -> None:
    async with get_sessionmaker()() as session:
        await session.execute(text("select 1"))
        checks["postgres"] = True
        result = await session.execute(text("select exists(select 1 from pg_extension where extname = 'vector')"))
        checks["pgvector"] = bool(result.scalar())
