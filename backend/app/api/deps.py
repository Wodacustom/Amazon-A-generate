"""API 依赖。"""

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import SystemUser
from app.services.security import decode_access_token


async def get_current_user(
    authorization: str | None = Header(default=None), db: AsyncSession = Depends(get_db)
) -> SystemUser:
    """从 Bearer token 解析当前用户。"""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")
    token = authorization.split(" ", 1)[1]
    try:
        # token 只携带 username 和 role；权限仍以数据库中的用户状态为准。
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    result = await db.execute(
        select(SystemUser).where(SystemUser.username == payload.get("sub"), SystemUser.deleted == 0)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")
    return user


async def require_admin(user: SystemUser = Depends(get_current_user)) -> SystemUser:
    """要求管理员角色。"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required.")
    return user
