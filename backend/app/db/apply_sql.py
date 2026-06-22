"""执行 SQL 初始化脚本。

Docker 后端容器启动时调用本模块，用 SQL 文件初始化数据库结构。
"""

import asyncio
import sys
from pathlib import Path

import asyncpg

from app.core.config import settings


def _asyncpg_url() -> str:
    """把 SQLAlchemy URL 转换成 asyncpg 可识别的 PostgreSQL URL。"""
    return settings.database_url.replace("postgresql+asyncpg://", "postgresql://")


def _read_sql(path: Path) -> str:
    """读取 SQL 文件内容。"""
    return path.read_text(encoding="utf-8")


async def apply_sql(path: Path) -> None:
    """连接数据库并执行 SQL 脚本。"""
    sql = _read_sql(path)
    connection = await asyncpg.connect(_asyncpg_url())
    try:
        # SQL 文件里没有函数体，asyncpg 可以一次性执行多条语句。
        await connection.execute(sql)
    finally:
        await connection.close()


def main() -> None:
    """命令行入口。"""
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m app.db.apply_sql <sql-file>")
    asyncio.run(apply_sql(Path(sys.argv[1])))


if __name__ == "__main__":
    main()
