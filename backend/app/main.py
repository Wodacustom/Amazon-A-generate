"""FastAPI 应用入口。

本模块负责创建应用、挂载中间件和注册 API 路由。
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware, configure_logging
from app.services.redis_client import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """管理应用生命周期，退出时释放 Redis 连接。"""
    yield
    await close_redis()


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    configure_logging()
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
    app.add_middleware(RequestLoggingMiddleware)
    # 前端开发端口较多，允许来源统一从配置读取。
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
