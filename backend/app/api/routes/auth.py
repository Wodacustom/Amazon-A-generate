"""认证接口。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import SystemUser
from app.schemas.auth import AuthTokenResponse, LoginRequest, UserRead
from app.services.security import create_access_token, verify_password

router = APIRouter()
logger = get_logger(__name__)


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> AuthTokenResponse:
    """登录并返回 access token。"""
    username = payload.username or payload.email
    if not username:
        logger.warning("auth.login.missing_username", extra={"event": "auth.login.missing_username"})
        raise HTTPException(status_code=400, detail="Username is required.")
    result = await db.execute(
        select(SystemUser).where(SystemUser.username == username, SystemUser.deleted == 0)
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password):
        logger.warning("auth.login.failed", extra={"event": "auth.login.failed", "username": username})
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    logger.info("auth.login.success", extra={"event": "auth.login.success", "username": user.username, "role": user.role})
    return AuthTokenResponse(accessToken=create_access_token(user.username, user.role), user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
async def me(user: SystemUser = Depends(get_current_user)) -> SystemUser:
    """当前用户。"""
    return user
